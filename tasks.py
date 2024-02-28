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
    #slowmo=1000
    )

    open_robot_order_website()
    close_annoying_modal()
    orders = get_orders()
    orders_table = convert_csv_to_a_table(orders)
    loop_through_orders(orders_table)

def open_robot_order_website():
    """
    Opens the robot order website.
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """
    Closes the welcome modal
    """
    page = browser.page()
    page.click("button:text('OK')")

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
    #close_annoying_modal()
    fill_the_form(order)
    info(order)
    print(f"{order}")
    
def fill_the_form(order):
    page = browser.page()
    page.select_option("id=head", order["Head"])
    page.locator("id=id-body-" + order['Body']).check()
    page.fill("//input[@placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("id=address", order["Address"])
    page.click("text=Preview")
    page.click("text=Order")