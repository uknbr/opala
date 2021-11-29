from cx_Freeze import setup, Executable

base = None    

executables = [
    Executable(
        "car.py",
        copyright="Copyright (C) 2020 Pedro Pavan",
        base=base,
        icon="olx.ico",
    ),
]

packages = ["idna", "colorama", "time", "sqlalchemy"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "OLX Car",
    options = options,
    version = "0.5.1",
    description = "Find your car now!",
    executables = executables
)