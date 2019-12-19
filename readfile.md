# How to install
First make sure you install python3 and to make sure
to add pip to the command line path.
### Open your favourite Terminal and run these commands.
To install all required dependencies just run :
```sh
$ pip3 install flask
```
When that is done make sure to unzip all files and maintain the directory layout

# How to use
> Just run the file called "maincode.py"

>Then open up your favourite browser and type into your url bar http://localhost:5000/ then click enter

> This should then load up the main page and you will be met with a table containing the list of tanks with the volumes and other properties

>You will also see six other buttons and these allow you to navigate to other pages on the webserver and these other pages will show you the features of the program

### The functions of each page:
#### Old-Sales data and predictions calculator
>This page allows you to see sales data and find predictions for specific times and if you want to you can also put in the recipe but that is not required
#### Fermenter
>With this page you can start a new brew by entering in a recipe a tank the number of bottles for the batch and the bottleID which keeps track of the batch
#### Conditioner
>Displays what is currently in the fermentation process and allows you to move them to the conditioner process
#### Storage
> Displays all the tanks and if they are in the conditioner process you can move them to storage when they are done
#### Inventory Tracker
>Displays which batches are in storage
#### Planner
>You can select which week to do the planning algorithm for and it will recommend based on what tanks are available if you should start brewing and uses data in storage to work out how many you should make
