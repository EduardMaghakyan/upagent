import asyncio
import time
from playwright.async_api import async_playwright
from datetime import datetime
from django.core.files.base import ContentFile
import logging
from asgiref.sync import sync_to_async

from flow_monitors.models import FlowMonitor, FlowCheck

logger = logging.getLogger(__name__)


async def run_flow(flow_monitor_id):
    try:
        # Get the flow
        # flow = FlowMonitor.objects.get(id=flow_monitor_id)

        flow = await sync_to_async(FlowMonitor.objects.get, thread_sensitive=True)(
            id=flow_monitor_id
        )

        start_time = time.time()
        error_message = None
        error_step = None
        screenshot = None
        is_successful = False

        logger.info(f"Starting flow check for: {flow.name} ({flow.id})")

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Start at the initial URL
            logger.info(f"Navigating to starting URL: {flow.starting_url}")
            await page.goto(flow.starting_url)

            flow_steps = await sync_to_async(flow.steps.all, thread_sensitive=True)()
            flow_steps = await sync_to_async(list, thread_sensitive=True)(flow_steps)

            for step in flow_steps:
                try:
                    logger.info(f"Executing step {step.sequence}: {step.description}")

                    if step.action_type == "navigate":
                        logger.info(f"Navigating to: {step.url}")
                        await page.goto(step.url)

                    elif step.action_type == "click":
                        # Use AI-friendly selectors based on text content
                        if step.element_description:
                            logger.info(
                                f"Clicking element with text: {step.element_description}"
                            )
                            try:
                                # Try exact text match first
                                await page.click(
                                    f'text="{step.element_description}"',
                                    timeout=step.timeout_seconds * 1000,
                                )
                            except Exception:
                                # If that fails, try contains
                                logger.info(
                                    f"Exact match failed, trying contains: {step.element_description}"
                                )
                                await page.click(
                                    f"text=/{step.element_description}/i",
                                    timeout=step.timeout_seconds * 1000,
                                )
                        else:
                            # Fallback if no description
                            logger.info(
                                "No element description, using generic selectors"
                            )
                            await page.click(
                                f'[aria-label="{step.description}"]',
                                timeout=step.timeout_seconds * 1000,
                            )

                    elif step.action_type == "fill":
                        # Find the field by various attributes
                        logger.info(
                            f"Filling field {step.element_description} with value: {step.input_value}"
                        )

                        # Try different selector strategies
                        selectors = [
                            f'[name="{step.element_description}"]',
                            f'[id="{step.element_description}"]',
                            f'[placeholder="{step.element_description}"]',
                            'input[type="text"]',  # Generic fallback
                            "textarea",  # Another fallback
                        ]

                        filled = False
                        for selector in selectors:
                            try:
                                logger.info(f"Trying selector: {selector}")
                                await page.fill(
                                    selector,
                                    step.input_value,
                                    timeout=step.timeout_seconds * 1000,
                                )
                                filled = True
                                break
                            except Exception as e:
                                logger.info(f"Selector {selector} failed: {str(e)}")
                                continue

                        if not filled:
                            raise Exception(
                                f"Could not find field to fill: {step.element_description}"
                            )

                    elif step.action_type == "wait":
                        logger.info(f"Waiting for element: {step.element_description}")
                        try:
                            # Try exact text match
                            await page.wait_for_selector(
                                f'text="{step.element_description}"',
                                timeout=step.timeout_seconds * 1000,
                            )
                        except Exception:
                            # Try contains match
                            await page.wait_for_selector(
                                f"text=/{step.element_description}/i",
                                timeout=step.timeout_seconds * 1000,
                            )

                    elif step.action_type == "verify":
                        logger.info(
                            f"Verifying element exists: {step.element_description}"
                        )
                        try:
                            # Try exact text match
                            element = await page.wait_for_selector(
                                f'text="{step.element_description}"',
                                timeout=step.timeout_seconds * 1000,
                            )
                        except Exception:
                            # Try contains match
                            element = await page.wait_for_selector(
                                f"text=/{step.element_description}/i",
                                timeout=step.timeout_seconds * 1000,
                            )

                        if not element:
                            raise Exception(
                                f"Element verification failed: {step.element_description}"
                            )

                    # Wait after action if specified
                    if step.wait_time_seconds > 0:
                        logger.info(
                            f"Waiting {step.wait_time_seconds} seconds after action"
                        )
                        await asyncio.sleep(step.wait_time_seconds)

                except Exception as e:
                    # Take screenshot on error
                    logger.error(f"Step failed: {str(e)}")
                    screenshot_bytes = await page.screenshot()
                    screenshot = ContentFile(
                        screenshot_bytes,
                        name=f"flow_{flow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    )

                    error_message = str(e)
                    error_step = step
                    break

            # Close browser
            await browser.close()

            # If we got here with no error_message, the flow was successful
            if not error_message:
                is_successful = True
                logger.info("Flow completed successfully")

            total_time = time.time() - start_time

            # Create check record
            check = FlowCheck(
                flow_monitor=flow,
                is_successful=is_successful,
                total_time=total_time,
                error_message=error_message,
                error_step=error_step,
            )

            # Save screenshot if we have one
            if screenshot:
                check.screenshot.save(
                    f"flow_{flow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    screenshot,
                    save=False,
                )

            await sync_to_async(check.save, thread_sensitive=True)()

            return {
                "flow_id": str(flow.id),
                "is_successful": is_successful,
                "total_time": total_time,
                "error_message": error_message,
                "error_step_id": str(error_step.id) if error_step else None,
            }

    except FlowMonitor.DoesNotExist:
        logger.error(f"Flow monitor with ID {flow_monitor_id} not found")
        return {"error": f"Flow monitor with ID {flow_monitor_id} not found"}
    except Exception as e:
        logger.exception(f"Error running flow {flow_monitor_id}: {str(e)}")
        return {"error": str(e)}
