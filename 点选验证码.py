import time
import logging
import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import base64
import json
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('captcha_login.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CaptchaCredentials:
    """Captcha service credentials"""
    username: str
    password: str

    @classmethod
    def from_env(cls) -> 'CaptchaCredentials':
        """Load credentials from environment variables"""
        return cls(
            username=os.getenv('CAPTCHA_USERNAME', 'npc1050'),
            password=os.getenv('CAPTCHA_PASSWORD', 'taotao123')
        )


@dataclass
class Config:
    """Configuration class with environment variable support"""
    # Website configuration
    BILIBILI_URL: str = 'https://www.bilibili.com/'

    # User credentials (load from environment variables for security)
    USERNAME: str = os.getenv('BILIBILI_USERNAME', '18318949605')
    PASSWORD: str = os.getenv('BILIBILI_PASSWORD', 'taotao123')

    # Wait times
    IMPLICIT_WAIT: int = 10
    EXPLICIT_WAIT: int = 20

    # File paths
    CAPTCHA_IMAGE_PATH: str = 'yzm.png'
    SAMPLE_IMAGE_PATH: str = 'yangban.png'

    # Captcha API configuration
    CAPTCHA_API_URL: str = "http://www.fdyscloud.com.cn/tuling/predict"
    CAPTCHA_ID: str = "47834707"
    CAPTCHA_VERSION: str = "3.1.1"


class CaptchaAPIError(Exception):
    """Custom exception for captcha API errors"""
    pass


class CaptchaAPI:
    """Handles captcha recognition API calls"""

    def __init__(self, credentials: CaptchaCredentials, config: Config):
        self.credentials = credentials
        self.config = config

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            raise CaptchaAPIError(f"Image file not found: {image_path}")
        except Exception as e:
            raise CaptchaAPIError(f"Failed to encode image {image_path}: {e}")

    def recognize_captcha(self, sample_path: str, captcha_path: str) -> Dict[str, Any]:
        """
        Recognize captcha using external API

        Args:
            sample_path: Path to sample image
            captcha_path: Path to captcha image

        Returns:
            API response dictionary

        Raises:
            CaptchaAPIError: If API call fails
        """
        try:
            b64_small = self._encode_image(sample_path)
            b64_large = self._encode_image(captcha_path)

            payload = {
                "username": self.credentials.username,
                "password": self.credentials.password,
                "ID": self.config.CAPTCHA_ID,
                "b64_small": b64_small,
                "b64_large": b64_large,
                "version": self.config.CAPTCHA_VERSION
            }

            response = requests.post(
                self.config.CAPTCHA_API_URL,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.info("Captcha recognition completed successfully")
            return result

        except requests.RequestException as e:
            raise CaptchaAPIError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise CaptchaAPIError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise CaptchaAPIError(f"Captcha recognition failed: {e}")


class BilibiliLoginBot:
    """Bilibili automated login bot"""

    def __init__(self, config: Config):
        self.config = config
        self.driver: Optional[webdriver.Edge] = None
        self.wait: Optional[WebDriverWait] = None
        self.captcha_api = CaptchaAPI(
            CaptchaCredentials.from_env(),
            config
        )

    @contextmanager
    def browser_context(self):
        """Browser context manager with proper cleanup"""
        try:
            # Configure browser options
            options = Options()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            self.driver = webdriver.Edge(options=options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, self.config.EXPLICIT_WAIT)

            logger.info(f"Browser window size: {self.driver.get_window_size()}")
            yield self.driver

        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("Browser closed successfully")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")

    def _wait_and_find_element(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        """Wait for and find element with error handling"""
        wait_time = timeout or self.config.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        try:
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            logger.error(f"Element not found within {wait_time}s: {locator}")
            raise

    def navigate_to_login(self) -> None:
        """Navigate to login page"""
        try:
            self.driver.get(self.config.BILIBILI_URL)
            self.driver.maximize_window()
            logger.info("Accessed Bilibili homepage")

            # Wait for and click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.bili-header .header-login-entry'))
            )
            login_button.click()
            logger.info("Login button clicked")

        except TimeoutException:
            logger.error("Login button loading timeout")
            raise

    def input_credentials(self) -> None:
        """Input username and password"""
        try:
            # Wait for login form to load
            username_input = self._wait_and_find_element(
                (By.CSS_SELECTOR, 'div.login-pwd-wp>form>div:nth-child(1)>input')
            )
            password_input = self.driver.find_element(
                By.CSS_SELECTOR, 'div.login-pwd-wp>form>div:nth-child(3)>input'
            )
            login_btn = self.driver.find_element(By.CSS_SELECTOR, 'div.btn_primary')

            # Clear and input credentials
            username_input.clear()
            username_input.send_keys(self.config.USERNAME)

            password_input.clear()
            password_input.send_keys(self.config.PASSWORD)

            # Click login
            login_btn.click()
            logger.info("Credentials entered and login button clicked")

        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to input credentials: {e}")
            raise

    def capture_captcha_images(self) -> None:
        """Capture captcha images"""
        try:
            # Wait for captcha to appear
            captcha_container = self._wait_and_find_element((
                By.CSS_SELECTOR,
                'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_table_box > div.geetest_window > div > div.geetest_item_wrap'
            ))

            sample_container = self.driver.find_element(
                By.CSS_SELECTOR,
                'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_head > div.geetest_tips > div.geetest_tip_img'
            )

            # Take screenshots
            captcha_container.screenshot(self.config.CAPTCHA_IMAGE_PATH)
            sample_container.screenshot(self.config.SAMPLE_IMAGE_PATH)
            logger.info(
                f"Captcha images saved: {self.config.CAPTCHA_IMAGE_PATH}, {self.config.SAMPLE_IMAGE_PATH}"
            )

        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to capture captcha images: {e}")
            raise

    def process_captcha(self) -> Dict[str, Any]:
        """Process captcha recognition"""
        try:
            result = self.captcha_api.recognize_captcha(
                self.config.SAMPLE_IMAGE_PATH,
                self.config.CAPTCHA_IMAGE_PATH
            )
            logger.info(f"Captcha recognition result: {result.get('data', 'No data')}")
            return result
        except CaptchaAPIError as e:
            logger.error(f"Captcha processing failed: {e}")
            raise

    def click_captcha_coordinates(self, captcha_result: Dict[str, Any]) -> bool:
        """
        Click captcha coordinates based on recognition result

        Args:
            captcha_result: Result from captcha recognition API

        Returns:
            bool: True if clicking succeeded, False otherwise
        """
        try:
            if captcha_result.get('code') != 1:
                logger.error(f"Captcha recognition failed: {captcha_result.get('message', 'Unknown error')}")
                return False

            data = captcha_result.get('data', {})
            if not data:
                logger.error("No coordinate data received from captcha API")
                return False

            # Get the captcha container element to calculate offset
            captcha_container = self.driver.find_element(
                By.CSS_SELECTOR,
                'body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_table_box > div.geetest_window > div > div.geetest_item_wrap'
            )

            # Get the container's location and size
            container_location = captcha_container.location
            container_size = captcha_container.size
            logger.info(f"Captcha container location: {container_location}")
            logger.info(f"Captcha container size: {container_size}")

            # Sort coordinates by order (顺序1, 顺序2, etc.)
            sorted_coordinates = []
            for i in range(1, len(data) + 1):
                order_key = f'顺序{i}'
                if order_key in data:
                    coord = data[order_key]
                    x = coord.get('X坐标值', 0)
                    y = coord.get('Y坐标值', 0)
                    sorted_coordinates.append((x, y))
                    logger.info(f"{order_key}: relative({x}, {y})")

            if not sorted_coordinates:
                logger.error("No valid coordinates found in captcha result")
                return False

            # Click coordinates in order using ActionChains with proper offset calculation
            for i, (x, y) in enumerate(sorted_coordinates, 1):
                try:
                    logger.info(f"Clicking coordinate {i}: relative({x}, {y})")

                    # Create new ActionChains instance for each click
                    actions = ActionChains(self.driver)

                    # Move to the element first, then move by offset and click
                    actions.move_to_element(captcha_container)
                    actions.move_by_offset(
                        x - container_size['width'] // 2,  # Adjust from center
                        y - container_size['height'] // 2  # Adjust from center
                    )
                    actions.click()
                    actions.perform()

                    logger.info(f"Successfully clicked coordinate {i}")
                    time.sleep(0.8)  # Slightly longer delay between clicks

                except Exception as click_error:
                    logger.error(f"Failed to click coordinate {i}: {click_error}")
                    # Try alternative method: direct coordinate clicking
                    try:
                        logger.info(f"Trying alternative click method for coordinate {i}")
                        abs_x = container_location['x'] + x
                        abs_y = container_location['y'] + y

                        actions = ActionChains(self.driver)
                        actions.move_by_offset(abs_x, abs_y)
                        actions.click()
                        actions.perform()

                        # Reset mouse position
                        actions = ActionChains(self.driver)
                        actions.move_by_offset(-abs_x, -abs_y)
                        actions.perform()

                        logger.info(f"Alternative click successful for coordinate {i}")
                        time.sleep(0.8)

                    except Exception as alt_error:
                        logger.error(f"Alternative click also failed for coordinate {i}: {alt_error}")
                        return False

            logger.info(f"Successfully clicked {len(sorted_coordinates)} coordinates")

            # Wait for the captcha to process
            time.sleep(3)

            return True

        except Exception as e:
            logger.error(f"Failed to click captcha coordinates: {e}")
            return False

    def run_to_captcha(self) -> bool:
        """Execute workflow up to captcha screenshot and clicking"""
        try:
            with self.browser_context():
                # 1. Navigate to login page
                self.navigate_to_login()
                time.sleep(3)

                # 2. Input credentials
                self.input_credentials()
                time.sleep(7)

                # 3. Capture captcha images
                self.capture_captcha_images()

                # 4. Process captcha
                captcha_result = self.process_captcha()

                # 5. Click captcha coordinates
                if self.click_captcha_coordinates(captcha_result):
                    logger.info("Captcha coordinates clicked successfully")

                    # Wait for potential login completion or next step
                    time.sleep(3)
                    pyautogui.click(x=1426, y=1084)

                    time.sleep(3)

                    # Check if login was successful or if there are additional steps
                    try:
                        # Look for potential success indicators or error messages
                        # This part may need adjustment based on Bilibili's actual response
                        logger.info("Waiting for login result...")
                        time.sleep(5)

                    except Exception as e:
                        logger.warning(f"Could not determine login status: {e}")

                else:
                    logger.error("Failed to click captcha coordinates")

                logger.info("Captcha workflow completed")

                # Keep browser open for user inspection
                input("Press Enter to close browser...")
                return True

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return False


def cleanup_files(config: Config) -> None:
    """Clean up temporary files"""
    try:
        Path(config.CAPTCHA_IMAGE_PATH).unlink(missing_ok=True)
        Path(config.SAMPLE_IMAGE_PATH).unlink(missing_ok=True)
        logger.info("Temporary files cleaned up")
    except Exception as e:
        logger.warning(f"File cleanup failed: {e}")


def main():
    """Main function"""
    config = Config()
    bot = BilibiliLoginBot(config)

    try:
        logger.info("Starting Bilibili login workflow (including captcha clicking)")
        success = bot.run_to_captcha()

        if success:
            logger.info("Login workflow completed successfully")
        else:
            logger.error("Login workflow failed")

    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"Program execution failed: {e}")
    finally:
        # Commented out file cleanup to preserve screenshot files
        # cleanup_files(config)
        pass


if __name__ == '__main__':
    main()
