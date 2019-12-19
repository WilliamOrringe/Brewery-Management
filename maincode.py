'''
Program allows you to manage the brewery tanks of the brewing tanks
and can allow you to make predictions and recommend how to act on processed
and saved data
'''
import csv
from datetime import datetime
import math
from flask import Flask, render_template, request, redirect
APP = Flask(__name__)
def read_sales_data():
    '''
    parse csv data into one dictionary for each line then an array for all then
    lines and then return the array of dictionaries
    '''
    sales_data = []
    with open("salesdata.csv", newline='') as sales_file:
        reader = csv.DictReader(sales_file)
        for row in reader:
            sales_data.append(row)
    sales_file.close()
    return sales_data
def split_by_recipe(sales_data):
    '''
    Splits data by recipe
    '''
    recipes = ["Organic Red Helles", "Organic Pilsner", "Organic Dunkel"]
    red_helles = []
    pilsner = []
    dunkel = []
    for line in sales_data:
        if line["Recipe"] == recipes[0]:
            red_helles.append(line)
        elif line["Recipe"] == recipes[1]:
            pilsner.append(line)
        else:
            dunkel.append(line)
    return red_helles, pilsner, dunkel
def categorise_months(specific_bottles, months):
    '''
    Categorises the number of sales per month
    '''
    month_bottle = []
    for _ in enumerate(months):
        month_bottle.append(0)
    for line in specific_bottles:
        for month_x, date_check in enumerate(months):
            if date_check in str(line["Date Required"]):
                month_bottle[month_x] += int(int(line["Quantity ordered"]) / 2)
    return month_bottle
def line_of_best_fit(month_bottle: list, month_predict):
    '''
    finds the line of best fit for the sales data and then outputs a prediction
    by using the equation and inputting a new x value therefore extrapolating
    '''
    y_bar = 0
    x_values = []
    x_total = 0
    month_bottle = month_bottle[1:]
    for i_counter in range(len(month_bottle)):
        x_values.append(i_counter+1)
        x_total += (i_counter+1)
    for line in month_bottle:
        y_bar += line
    y_bar /= len(month_bottle)
    x_bar = x_total / len(month_bottle)
    numerator = 0
    denominator = 0
    for counter, tank_name_set in enumerate(month_bottle):
        numerator += (tank_name_set * (x_values[counter])) - \
        (x_bar * y_bar)
        denominator += (x_values[counter])** 2 - (x_bar**2)
    gradient = numerator / denominator
    y_intercept = y_bar - (gradient * x_bar)
    y_value = (float(month_predict) * float(gradient)) + y_intercept
    return y_value
def inner_logic_post(names_of_beer, months_of_bottles, dates_stuff=None,\
                    recipe_stuff=None):
    '''
    allows the planner to access this as it couldn't if inside other function as
    it would not be a POST method and this section of code just returns a the
    list of predictions made by the line_of_best_fit function above
    '''
    predictions = []
    if dates_stuff and recipe_stuff is not None:
        month_pred = (dates_stuff)
        recipe_stuff = int(recipe_stuff) - 1
        predictions.append(str(names_of_beer[recipe_stuff]) + ": " + \
        str(int(line_of_best_fit(months_of_bottles[recipe_stuff],\
         month_pred))))
    elif dates_stuff is not None:
        month_pred = (dates_stuff)
        for bottle_num, big_change in enumerate(months_of_bottles):
            predictions.append(str(names_of_beer[bottle_num]) + ": " + \
            str(int(line_of_best_fit(big_change,\
            month_pred))))
    return predictions
@APP.route('/predictions', methods=['POST', 'GET'])
def predictions_func(yug1=None, yug2=None):
    '''
    finds the predicted value at a specific date and if the recipe is not
    specified returns all of the recipes
    '''
    months = ["Nov-18", "Dec-18", "Jan-19", "Feb-19", "Mar-19", "Apr-19",\
    "May-19", "Jun-19", "Jul-19", "Aug-19", "Sep-19", "Oct-19"]
    names_of_beer = ["Red Helles", "Pilsner", "Dunkel"]
    column_heads = ["Bottle Name"]
    column_heads += months
    saledata = read_sales_data()
    red_helless, pilsners, dunkels = split_by_recipe(saledata)
    months_of_bottles = []
    months_of_bottles.append(["Red Helles"] + \
    categorise_months(red_helless, months))
    months_of_bottles.append(["Pilsner"] + categorise_months(pilsners, months))
    months_of_bottles.append(["Dunkel"] + categorise_months(dunkels, months))
    predictions = []
    month_pred = 12
    if request.method == 'POST':
        dates_stuff = request.form.get('time_period')
        recipe_stuff = request.form.get('recipe_type')
        if dates_stuff is not None:
            month_pred = dates_stuff
        predictions = inner_logic_post(names_of_beer, months_of_bottles, \
        dates_stuff, recipe_stuff)
    else:
        month_pred = 12
        for bottle_num, blast in enumerate(months_of_bottles):
            predictions.append(str(names_of_beer[bottle_num]) + ": " + str\
            (int(line_of_best_fit(blast,\
             month_pred))))
    month_temp = float(month_pred)
    month_pred = math.floor(month_temp)
    month_preds = months[int(month_pred % 12)][:3]
    tm_mon = datetime.strptime(str(month_preds), '%b')
    tm_now = datetime.strftime(tm_mon, '%B')
    month_preds = str(tm_now) + "("+str(int((month_temp-12) * 4))\
    + " week/s from now)"
    if yug1 is None:
        return render_template("prediction_page.html", \
        bottleasd=months_of_bottles, months=column_heads, \
        predictions=predictions, month_predict=month_preds)
    predictions = inner_logic_post(names_of_beer, months_of_bottles, yug1, \
    yug2)
    return predictions
@APP.route('/fermentation', methods=["POST", "GET"])
def fermentation():
    '''
    fermentation tracker; works by changing the values in the text file to
    show that it is now active and with the 'Fermentation' extension
    '''
    if reading_file() == []:
        brewing_list = setup_tanks()
    else:
        brewing_list = reading_file()
    brewing_names = []
    for brews in brewing_list:
        if "Fermenter" in brews[2] and "Active" not in brews[3]:
            brewing_names.append(brews[0])
    writing_brewing_file(brewing_list)
    if request.method == 'POST':
        recipe_type = request.form.get('recipe_type')
        tank_type = request.form.get('tank_type')
        bottle_id = request.form.get('bottle_id')
        number_of_bottles = request.form.get('bottle_number')
        tank_type = str(tank_type)
        if recipe_type is not None and tank_type is not None and\
        int(number_of_bottles) > 0:
            for brews in brewing_list:
                if tank_type == brews[0]:
                    select_value = brews
                    select_value[3] = "Active-Fermentation"
                    tm_mon = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
                    select_value[4] = tm_mon
                    total_vol = select_value[1]
                    if int(total_vol) >= int(number_of_bottles):
                        writing_batch_file(tank_type, bottle_id, recipe_type,\
                        number_of_bottles)
                        brews = select_value
                    else:
                        select_value[3] = "No"
                        select_value[4] = "N/A"
        brewing_names = []
        for brews in brewing_list:
            if "Fermenter" in brews[2] and "Active" not in brews[3]:
                brewing_names.append(brews[0])
        writing_brewing_file(brewing_list)
    return render_template("fermentation.html", brew_l=brewing_names, \
    new_title="Schedule new order")
def writing_brewing_file(brewing_list):
    '''
    write to the brew list file
    '''
    with open('brew_list.txt', 'w+') as f_write:
        for brews in brewing_list:
            f_write.write(str(brews) + "\n")
    f_write.close()
def writing_batch_file(tank_type, bottle_id, recipe_type, number_of_bottles):
    '''
    write to the batches file
    '''
    with open('batches.txt', 'a+') as f_write:
        f_write.write(str(tank_type) + ":" + str(bottle_id) \
        + ":" +str(recipe_type) + ":" +str(number_of_bottles) +"\n")
    f_write.close()
def reading_file():
    '''
    returns data from brew_list.txt
    '''
    brewing_list = []
    with open('brew_list.txt', 'r+') as f_read:
        for line in f_read:
            temp_value = line.strip('\n').replace(' ', '').replace('[', '').\
            replace(']', '').replace('"', '').replace("'", "").split(',')
            brewing_list.append(temp_value)
    f_read.close()
    return brewing_list
def reading_batch_file(tank_type=None):
    '''
    reads from batches.txt and returns as list
    '''
    batch_list = []
    with open('batches.txt', 'r+') as f_read:
        for line in f_read:
            if tank_type is not None:
                if str(tank_type) in line.strip("\n").split(":"):
                    batch_list.append(line.strip("\n"))
            else:
                if(line != "" or line != "\n"):
                    batch_list.append(line.strip("\n"))
    f_read.close()
    return batch_list
def setup_tanks():
    '''
    Defines the brew list with data given from specification
    '''
    brew_list = [['R2D2', 800, 'Fermenter', 'No', 'N/A'],\
                ['Albert', 1000, 'Fermenter/conditioner', 'No', 'N/A'],\
                ['Brigadier', 800, 'Fermenter/conditioner', 'No', 'N/A'],\
                ['Dylon', 800, 'Fermenter/conditioner', 'No', 'N/A'],\
                ['Emily', 1000, 'Fermenter/conditioner', 'No', 'N/A'],\
                ['Florence', 800, 'Fermenter/conditioner', 'No', 'N/A'],\
                ['Gertrude', 680, 'Conditioner', 'No', 'N/A'],\
                ['Harry', 680, 'Conditioner', 'No', 'N/A']]
    return brew_list
@APP.route('/tracking', methods=["POST", "GET"])
def tracking():
    '''
    displays what is in each tank
    '''
    brewing_list = ()
    column_heads = ["Name", "Volume", "Type", "Active-Stage", "Time started"]
    return render_template("tank_tracker.html", brew_l=brewing_list,\
      col_h=column_heads)
@APP.route('/conditioning', methods=["POST", "GET"])
def conditioning():
    '''
    conditioning display
    '''
    if reading_file() == []:
        brewing_list = setup_tanks()
    else:
        brewing_list = reading_file()
    brewing_names = []
    column_heads = ["Tank", "BottleID", "Recipe", "Quantity of Bottles", \
    "Time-Elapsed"]
    old_batch_list = reading_batch_file()
    batch_list = []
    temp_hold = []
    for batches in old_batch_list:
        temp_hold = str(batches).split(":")
        batch_list.append(temp_hold)
    if batch_list == []:
        column_heads = ["All tanks are inactive"]
    else:
        for row in batch_list:
            for item in brewing_list:
                if item[0] in row:
                    row.append(item[4])
    return render_template("conditioning.html", brew_l=brewing_names, \
    new_title="Select brew for conditioning", batch_list=batch_list, \
    col_h=column_heads, brewing_list=brewing_list)
@APP.route('/conditioning/<name>', methods=["POST", "GET"])
def condition_mode(name):
    '''
    conditioning tracker; works by changing the values in the text file to
    show that it is now active and with the 'Conditioning' extension also if
    changing tanks it changes where the batches are in i.e. changing name
    '''
    brew_list = reading_file()
    store_r2 = []
    big_temp_list = []
    temp_list = brew_list + []
    for line in temp_list:
        if line[0] == "R2D2":
            store_r2 = line
            temp_list.remove(line)
            big_temp_list = temp_list + []
    if request.method == "POST":
        batch_list = reading_batch_file()
        name_new = str(request.form.get('tank_type'))
        name_new = name_new.split(',')
        name_new = name_new[0]
        name_new = name_new.replace("'", "").replace('[', '')
        for batch in batch_list:
            new_item = batch.split(":")
            if name == new_item[0]:
                new_batch_list = (str(name_new) + ":" + new_item[1] + ":" + \
                new_item[2] + ":" + new_item[3])
                simple_write_to_batch(new_batch_list)
        new_name = str(request.form.get('tank_type'))
        new_name = new_name.split(',')
        new_name = new_name[0]
        new_name = new_name.replace("'", "").replace('[', '')
        for row in temp_list:
            if new_name == row[0]:
                row[3] = "Active-Conditioning"
                row[4] = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
            if name == row[0]:
                row[3] = "No"
                row[4] = "N/A"
        if name == "R2D2":
            store_r2[3] = "No"
            store_r2[4] = "N/A"
        temp_list.append(store_r2)
        brew_list = temp_list
        writing_brewing_file(brew_list)
    return render_template("select_tank.html", brew_l=big_temp_list)
@APP.route('/tank/<name_of_tank>')
def check_tank(name_of_tank):
    '''
    checks what is in the tank and shows it to the user
    '''
    batch_list = reading_batch_file(name_of_tank)
    column_heads = ["BottleID", "Recipe", "Quantity of Bottles"]
    new_row = []
    for batch in batch_list:
        temp = batch.split(":")
        new_row.append(temp[1:])
    name_of_tank = str(name_of_tank)
    if batch_list == []:
        column_heads = ["This tank is currently inactive"]
    return render_template("tank_tracker.html", name_t=name_of_tank, \
    col_h=column_heads, brew_l=new_row, new_title="Tank Tracker")
@APP.route('/storage')
def storage():
    '''
    checks if anything is in storage and returns it
    '''
    column_heads = ["Tank Name", "Recipe", "Quantity of Bottles", "Active", \
    "Time-Started"]
    new_row = reading_file()
    if new_row == []:
        column_heads = ["Nothing in storage"]
    return render_template("storage.html", new_title="Inventory Checker", \
    col_h=column_heads, batch_list=new_row)
@APP.route('/storage/<name_to_be_added>')
def storages(name_to_be_added):
    '''
    adds a batch to the storage if finished conditioning
    '''
    new_row = reading_file()
    storage_rows = reading_batch_file()
    temp_list = []
    for row in new_row:
        if row[0] == name_to_be_added and row[3] == "Active-Conditioning":
            row[3] = "No"
            row[4] = "N/A"
        temp_list.append(row)
    writing_brewing_file(temp_list)
    for row in storage_rows:
        if name_to_be_added in row:
            temp_list = row
            write_to_storage(temp_list)
            row = ""
        simple_write_to_batch(row)
    return redirect('/storage')
def write_to_storage(inventory_list):
    '''
    writes to storage.txt
    '''
    with open('storage.txt', 'a+') as f_write:
        f_write.write(str(inventory_list) + "\n")
    f_write.close()
def simple_write_to_batch(inventory_list):
    '''
    writes one string to batch file which is used for editing values in it
    '''
    with open('batches.txt', 'w+') as f_write:
        f_write.write(str(inventory_list) + "\n")
    f_write.close()
def reading_storage_file(tank_type=None):
    '''
    reads storage file and returns it as a list
    '''
    batch_list = []
    with open('storage.txt', 'r+') as f_read:
        for line in f_read:
            if tank_type is not None:
                if str(tank_type) in line.strip("\n").split(":"):
                    batch_list.append(line.strip("\n"))
            else:
                batch_list.append(line.strip("\n"))
    f_read.close()
    return batch_list
@APP.route('/inventory', methods=["POST", "GET"])
def inventory():
    '''
    Displays if anything if any batches are in the inventory
    '''
    column_heads = ["BottleID", "Recipe", "Quantity of Bottles"]
    new_rows = reading_storage_file()
    new_row = []
    for row in new_rows:
        new_row.append(row.split(":")[1:])
    if new_rows == []:
        column_heads = ["Nothing in storage"]
    return render_template("tank_tracker.html", new_title="Inventory Checker", \
    col_h=column_heads, brew_l=new_row)
@APP.route('/planner', methods=["POST", "GET"])
def planner():
    '''
    does the recommendations for brewing or not brewing and works out how many
    should be made if it wants to recommend it
    '''
    months = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr",\
    "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    number_ferm = 0
    number_cond = 0
    new_total = 0
    month_now = 0
    name = ""
    personal_msg = ""
    temp_store = 0
    list_of_processors = reading_file()
    for item in list_of_processors:
        if item[3] == "Active-Fermentation":
            number_ferm += 1
        elif item[3] == "Active-Conditioning":
            number_cond += 1
    if (number_ferm + number_cond) > (len(list_of_processors) - 3):
        recommend = False
        personal_msg = "It is not recommended to start brewing at this time"
    else:
        recommend = True
        personal_msg = "It is recommended to start brewing at this time"
    month_conv = 0
    if request.method == "POST":
        if recommend and request.form.get('month_id') is not None:
            month_id = request.form.get('month_id')
            predictions = []
            month_now = float(month_id) + 12
            predictions = predictions_func(month_now)
            month_now -= 12
            month_conv += (int(month_now))
            month_conv = int(month_conv)
            biggest_value = 0
            indexs = 0
            new_name_max = "Red Helles"
            for index, values in enumerate(predictions):
                new_name = ''.join([i for i in values if not i.isdigit()])
                if int(values.replace(new_name, "")) > int(biggest_value):
                    biggest_value = values.replace(new_name, "")
                    indexs = index
                    new_name_max = new_name.replace(" ", "").replace(":", "")
            name = new_name_max
            value = int(predictions[indexs].replace(name + ": ", ""))
            bottle_list = reading_storage_file()
            for line in bottle_list:
                name_bottle = line.split(":")
                if name_bottle[2] == name:
                    new_total += int(name_bottle[3])
            temp_store = new_total
            new_total = value - new_total
    month_now = int(month_now)
    return render_template("planner.html", new_tot=new_total, months=months\
                            , p_m=personal_msg, month_conv=month_now, \
                            n_bottles=name, storage=temp_store)
@APP.route('/', methods=["POST", "GET"])
def main_page():
    '''
    displays the main page and updates the brew_list.txt
    '''
    if reading_file() != []:
        brewing_list = reading_file()
    else:
        brewing_list = setup_tanks()
        writing_brewing_file(brewing_list)
    column_heads = ["Name", "Volume", "Type", "Active-Stage", "Time started"]
    return render_template("main_page.html", brew_l=brewing_list,\
      col_h=column_heads)
if __name__ == "__main__":
    APP.run(debug=True, use_reloader=True)
