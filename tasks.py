from robocorp.tasks import task
from robocorp import browser
import requests
from RPA.Tables import Tables
from robocorp.log import critical, warn, info, debug, exception

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
    orders_table = convert_csv_to_a_table(orders)
    loop_through_orders(orders_table)

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

def convert_csv_to_a_table(csv_file):
    library = Tables()
    orders_table = library.read_table_from_csv(csv_file, columns=["Order number", "Head", "Body", "Legs", "Address"])
    return orders_table

def loop_through_orders(orders_table):
    """
    Loop through the orders table and place an order for each row.
    """
    for order in orders_table:
        place_an_order(order)

def place_an_order(order):
    """
    Places a single order and saves the receipt along with an image of the robot
    """
    #info(order)
    print(f"{order}")
    