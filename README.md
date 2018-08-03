# Sit

> Let there be your flask application deployed with one command.

## Quick Overview

```sh
sit create my-app
cd my-app
source venv/bin/activate
sit init
sit deploy
```

Then open [your server address] to see your app.<br />
Next time you want to deploy with some modification just run `sit deploy` and you're done.

## Installation

```sh
pip install sit
```

`sit` works fine as long as it is included in your `$PATH` but if you're not familiar with this concept, you'll find it most comfortable to just install it globally.

## Creating an App

To create a new app, run following command:

```sh
sit create my-app
```

It will create a directory called `my-app` inside the current folder.

(Note: You can skip this step if you already have a working project.<br />
Jump to [`sit init`](#sit-init) deploy your old project easier.)


Inside that directory, it will generate the initial project structure and install the transitive dependencies:

```
my-app
├── README.md
├── setup.cfg
├── setup.py
├── .gitignore
├── .python-version
├── venv
├── requirements.txt
└── my-app
    ├── static
    │   └── index.css
    ├── temapltes
    │   └── index.html
    └── __init__.py
```

No configuration or complicated folder structure, just the files you need to build your app.

Once the installation is done, you can open your project folder:

```sh
cd my-app
```

and activate virtual environment for your flask app:

```sh
source venv/bin/activate
```

Now, inside the newly created project, you can run some built-in commands:

### `flask run`

Runs the app in development mode.<br />
Open [http://localhost:5000](http://localhost:5000) to view it in the browser.

The page will automatically reload if you make changes to the code.

### `sit init`


## License

Sit is open source software [licensed as MIT]()
