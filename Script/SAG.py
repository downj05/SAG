import os
import random
import string
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import discord
from selenium_stealth import stealth
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from colorama import init, Fore, Back, Style
import traceback
import argparse
import yaml


parser = argparse.ArgumentParser()
parser.add_argument(
    "-e",
    "--emails",
    help="File to read emails from, email will be removed from file after use",
    required=False,
)
parser.add_argument(
    "-w", "--webhooktest", help="Test webhook", required=False, action="store_true"
)

parser.add_argument(
    "-c", "--config", help="Config file", required=False, default="config.yml"
)

args = parser.parse_args()

init(autoreset=True)

# Import config.yml
with open(args.config, "r") as f:
    config = yaml.safe_load(f)

WEBHOOK_URL = config["webhook"]
if WEBHOOK_URL == "" or WEBHOOK_URL is None:
    print("Please enter a discord webhook url in webhook.txt")
    exit(1)
WEBHOOK_BRAND = config["webhook_brand"]
if WEBHOOK_BRAND == "" or WEBHOOK_BRAND is None:
    WEBHOOK_BRAND = "W32 Account Generator"

FACES = ["x3", ":(", ">.<", ":P"]

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value]

user_agent_rotator = UserAgent(
    software_names=software_names, operating_systems=operating_systems, limit=100
)


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
    def __init__(self, url):
        self.url = url
        print("Creating driver")
        self.driver = webdriver.Chrome(options=chrome_options)
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

    def wait_for_click(self, xpath: str):
        print("Waiting for click on " + xpath)
        while True:
            try:
                self.driver.find_element(By.XPATH, xpath).click()
                break
            except:
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


def send_to_webhook(email, username, password):
    webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
    embed = discord.Embed(title="New Steam Account!", color=0xEE00FF)
    embed.set_author(name=f"{WEBHOOK_BRAND} Account Generator")
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Password", value=password, inline=True)
    embed.add_field(name="Email", value=email, inline=False)
    webhook.send(embed=embed)


def test_webhook():
    webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
    embed = discord.Embed(
        title="Webhook Test",
        description="This is a test for the webhook feature of the account generator.",
        color=0xA6A6A6,
    )
    embed.set_author(name=f"{WEBHOOK_BRAND} Account Generator")
    embed.set_footer(text=random.choice(FACES))
    webhook.send(embed=embed)


def error_webhook(email, username, password, error):
    webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
    embed = discord.Embed(
        title=f"Error Making Account! {random.choice(FACES)}",
        description="Posting error so we don't lose the credentials incase the account was already made!",
        color=0xFF0000,
    )
    embed.set_author(name=f"{WEBHOOK_BRAND} Account Generator")
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Password", value=password, inline=True)
    embed.add_field(name="Email", value=email, inline=False)
    embed.set_footer(text=error)
    webhook.send(embed=embed)


def random_string(length):
    pool = string.ascii_letters + string.digits
    return "".join(random.choice(pool) for i in range(length))


# GENERATOR
def create_steam_account(email, username, password):
    try:
        print(
            f"{Fore.LIGHTYELLOW_EX}Making account with {email} | {username} | {password}"
        )
        bot = Bot(url=url)
        bot.enter_field('//*[@id="email"]', email)
        bot.enter_field('//*[@id="reenter_email"]', email)

        bot.wait_for_click('//*[@id="i_agree_check"]')

        prompt = "PLEASE COMPLETE THE CAPTCHA AND EMAIL VERIFICATION AND PRESS CONTINUE ON THE SITE"
        print(Fore.LIGHTCYAN_EX + "#" * len(prompt))
        print(Style.BRIGHT + Fore.WHITE + prompt)
        print(Fore.LIGHTCYAN_EX + "#" * len(prompt))
        input(Fore.MAGENTA + "Press enter once finished." + Style.RESET_ALL)
        bot.wait_for_click_css("div.create_newaccount_ctn > button", timeout=2)

        bot.enter_field('//*[@id="accountname"]', username)
        bot.enter_field('//*[@id="password"]', password)
        bot.enter_field('//*[@id="reenter_password"]', password)
        sleep(1)
        bot.wait_for_click('//*[@id="createAccountButton"]')
        sleep(1)
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "Account successfully created")
        print(f"Username: {username} | Password: {password} | Email: {email}")
        send_to_webhook(email, username, password)
        bot.close()
    except Exception as error:
        print(Fore.RED + "Error making account!", error)
        error_webhook(email, username, password, error)
        traceback.print_exc()


try:
    if args.webhooktest:
        print("Testing webhook...")
        try:
            test_webhook()
            print(Fore.GREEN + "Webhook test successful!")
        except Exception as err:
            print(Fore.RED + "Webhook test failed!")
            print(err)
            exit(1)
        exit(0)
    if args.emails:
        with open(args.emails, "r") as f:
            emails = f.read().strip().splitlines()

    for i in range(0, int(input("How many accounts to make?:"))):
        if not args.emails:
            email = input("Email:")
        else:
            email = emails.pop(0)
            with open(args.emails, "w") as f:
                f.write("\n".join(emails))
        create_steam_account(
            email,
            username=random_string(16),
            password=random_string(32),
        )
except Exception as err:
    print(err)
    print("Press any key to close the program...")
    input()
