from robocorp.tasks import task
from robocorp import browser
import requests
from RPA.Tables import Tables
from robocorp.log import critical, warn, info, debug, exception

orders_table = []

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images. 
    """
    browser.configure(
    browser_engine="chrome",
    headless=False,
    slowmo=1000
    )

    open_robot_order_website()
    orders = get_orders()
    convert_csv_to_a_table()

def open_robot_order_website():
    """
    Opens the robot order website.
    """
    browser.goto("https://robotsparebinindustries.com/")

def get_orders():
    """
    Downloads the orders file
    """
    response = requests.get("https://robotsparebinindustries.com/orders.csv")
    response.raise_for_status() # This will raise an exception if the request fails
    with open("orders.csv", 'wb') as stream:
        stream.write(response.content)
    return "orders.csv"

def convert_csv_to_a_table():
    library = Tables()
    orders_table = library.read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"])
    #print(orders_table)
