import os
import random
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import discord
from selenium_stealth import stealth
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from colorama import init, Fore, Back, Style
import traceback


init(autoreset=True)

FACES = ["x3", ":(", ">.<", ":P"]

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value]

user_agent_rotator = UserAgent(
    software_names=software_names, operating_systems=operating_systems, limit=100
)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


chrome_options = Options()
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

version = "2.2"
url = "https://store.steampowered.com/join"
path = os.path.dirname(os.path.realpath(__file__))


def chunks(xs, n):
    n = max(1, n)
    return (xs[i : i + n] for i in range(0, len(xs), n))


class Bot:
    def __init__(self, url, chrome_executable_path=None):
        self.url = url
        print("Creating service")
        s = Service(executable_path=chrome_executable_path)
        print("Creating driver")
        self.driver = webdriver.Chrome(service=s, options=chrome_options)

        print("Applying stealth")
        user_agent = user_agent_rotator.get_random_user_agent()
        print(user_agent)
        stealth(
            self.driver,
            languages=["en-US", "en"],
            user_agent=user_agent,
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        print("Going to url")
        self.driver.get(self.url)

    def wait_for_element(self, xpath: str, timeout=4):
        print("Waiting for element " + xpath)
        s = time()
        while True:
            try:
                self.driver.find_element(By.XPATH, xpath)
                break
            except:
                sleep(0.5)
            finally:
                if time() - s > timeout:
                    print("Skipping because timeout")
                    break

    def wait_for_element_css(self, selector: str, timeout=4) -> 'Element':
        print("Waiting for element " + selector)
        s = time()
        while True:
            try:
                e = self.driver.find_element(By.CSS_SELECTOR, selector)
                return e
                break
            except:
                sleep(0.5)
            finally:
                if time() - s > timeout:
                    print("Skipping because timeout")
                    break

    def wait_for_click(self, xpath: str):
        print("Waiting for click on " + xpath)
        while True:
            try:
                self.driver.find_element(By.XPATH, xpath).click()
                break
            except Exception as e:
                print(f"got {e} while waiting for {xpath}")
                sleep(0.5)

    def wait_for_click_css(self, selector: str, timeout=4):
        print("Waiting for click on " + selector)
        s = time()
        while True:
            try:
                self.driver.find_element(By.CSS_SELECTOR, selector).click()
                print("Clicked on " + selector)
                break
            except:
                sleep(0.5)
            finally:
                if time() - s > timeout:
                    print("Skipping because timeout")
                    break

    def enter_field(self, xpath: str, text: str):
        self.wait_for_click(xpath)
        self.wait_for_type(xpath, text)
        return

    def wait_for_type(self, xpath: str, text: str):
        print("Typing " + text + " into " + xpath)
        while True:
            try:
                e = self.driver.find_element(By.XPATH, xpath)
                break
            except:
                sleep(0.5)
        for x in chunks(text, 4):
            e.send_keys(x), sleep(random.uniform(0, 0.05))
        return

    def close(self):
        self.driver.close()

class Webhook:
    def __init__(self, webhook_url: str, brand: str="No Brand") -> None:
        self.brand = brand
        self. webhook = discord.SyncWebhook.from_url(webhook_url)


    def send_to_webhook(self,email, username, password, steam_url=None, steam_id=None):
        embed = discord.Embed(title="New Steam Account!", color=0xEE00FF)
        embed.set_author(name=self.brand)
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Password", value=f"||{password}||", inline=True)
        embed.add_field(name="Email", value=email, inline=False)
        if steam_url:
            embed.add_field(name="Steam URL", value=steam_url, inline=False)
        if steam_id:
            embed.add_field(name="Steam ID", value=steam_id, inline=False)
        self.webhook.send(embed=embed)

    def test_webhook(self):
        embed = discord.Embed(
            title="Webhook Test",
            description="This is a test for the webhook feature of the account generator.",
            color=0xA6A6A6,
        )
        embed.set_author(name=self.brand)
        embed.set_footer(text=random.choice(FACES))
        embed.add_field(name="Test", value="specialspecial123 [burger](https://burger.com)", inline=False)
        self.webhook.send(embed=embed)


    def error_webhook(self, email, username, password, error):
        embed = discord.Embed(
            title=f"Error Making Account! {random.choice(FACES)}",
            description="Posting error so we don't lose the credentials incase the account was already made!",
            color=0xFF0000,
        )
        embed.set_author(name=self.brand)
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Password", value=password, inline=True)
        embed.add_field(name="Email", value=email, inline=False)
        embed.set_footer(text=error)
        self.webhook.send(embed=embed)



# GENERATOR
def create_steam_account(email, username, password, webhook: Webhook=None):
    try:
        print(
            f"{Fore.LIGHTYELLOW_EX}Making account with {email} | {username} | {password}"
        )
        bot = Bot(url=url)
        bot.enter_field('//*[@id="email"]', email)
        bot.enter_field('//*[@id="reenter_email"]', email)

        bot.wait_for_click('//*[@id="i_agree_check"]')

        prompt = "PLEASE COMPLETE THE CAPTCHA AND EMAIL VERIFICATION"
        print(Fore.LIGHTCYAN_EX + "#" * len(prompt))
        print(Style.BRIGHT + Fore.WHITE + prompt)
        print(Fore.LIGHTCYAN_EX + "#" * len(prompt))
        bot.wait_for_click_css("div.create_newaccount_ctn > button", timeout=1200)

        bot.enter_field('//*[@id="accountname"]', username)
        bot.enter_field('//*[@id="password"]', password)
        bot.enter_field('//*[@id="reenter_password"]', password)
        sleep(1)
        bot.wait_for_click('//*[@id="createAccountButton"]')
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "Account successfully created")
        print(f"Username: {username} | Password: {password} | Email: {email}")
        e = bot.wait_for_element_css('a.user_avatar', timeout=25)
        print(e)
        steam_url = e.get_attribute('href')
        print(steam_url)
        steam_id = steam_url.split('/profiles/')[1].replace('/', '')
        if webhook:
            webhook.send_to_webhook(email, username, password, steam_url=steam_url, steam_id=steam_id)
        bot.close()
    except Exception as error:
        print(Fore.RED + "Error making account!", error)
        if webhook:
            webhook.error_webhook(email, username, password, error)
        traceback.print_exc()
        raise error
