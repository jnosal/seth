Example of using seth comand utility.

Just create manage.py file and register your commands in it.
After that simply run:

python manage.py path_to_ini_file command_name optionally_command_args

with our super_command file:

python manage.py conf.ini super_command --verbose=true