from robocorp.tasks import task
from robocorp import browser
import requests
from RPA.Tables import Tables
from robocorp.log import critical, warn, info, debug, exception
from RPA.PDF import PDF
from RPA.Archive import Archive

pdf = PDF()

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
    headless=True,
    #slowmo=1000
    )

    open_robot_order_website()
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
    close_annoying_modal()
    fill_the_form(order)
    
def fill_the_form(order):
    """
    Fills the order form and makes the purchase
    """
    page = browser.page()
    page.select_option("id=head", order["Head"])
    page.locator("id=id-body-" + order['Body']).check()
    page.fill("//input[@placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("id=address", order["Address"])
    page.locator("#preview").click()
    page.locator("#order").click()
    while page.locator("#order").count() > 0:
        page.locator("#order").click()
    order_number = page.locator(".badge-success").text_content()
    order_pdf_path = store_receipt_as_pdf(order_number)
    print(f"Order pdf path: {order_pdf_path}")
    robot_image = screenshot_robot(order_number)
    embed_screenshot_to_receipt(robot_image, order_pdf_path)
    archive_receipts()
    page.locator("id=order-another").click()

def store_receipt_as_pdf(order_number):
    """
    Saves the purchase receipt to a pdf. Pdf name contains the order number.
    """
    page = browser.page()
    pdf.html_to_pdf(page.inner_html("id=receipt"), f"output/receipts/{order_number}.pdf")
    return f"output/receipts/{order_number}.pdf"

def screenshot_robot(order_number):
    """
    Saves an image of the robot that was ordered
    """
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path=f"output/screenshots/{order_number}.png")
    return f"output/screenshots/{order_number}.png"

def embed_screenshot_to_receipt(screenshot, order_pdf_path):
    """
    Embeds the image of the robot that was ordered to the receipt pdf
    """
    pdf.add_files_to_pdf(files = [screenshot], target_document = f"{order_pdf_path}", append = True)

def archive_receipts():
    """
    Archives all the receipts to a single zip file to the output folder
    """
    archive_library = Archive()
    archive_library.archive_folder_with_zip(folder="output/receipts", archive_name="output/receipts.zip", include="*.pdf")

