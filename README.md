# Sit

> Let there be your flask application deployed with one command.

## Quick Overview

```sh
sit create my-app
cd my-app
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

Configures your project to be deployed anytime.<br />
It will ask you some information about your remote server and then save them into `.sit/config.json`.

`.sit` folder contains all the configuration files, built source distributions etc.<br />

You can run this command on previously existing project without any problem, if your flask application is packed into a package, like the one created by `sit create`. [Working with your old projects](#working-with-your-old-projects)

### `sit deploy`

Deploys your flask application to the remote server.<br />
If you run this command for the first time, it will automatically set up the remote server too.

After then, your flask application is online!

### `sit setup`

Sets up the remote server to be ready for deployment.<br />
Since `sit deploy` sets up the server too when it's called for the first time, it won't be necessary in usual cases. But you can do it anyway if you want.

### Working with your application

Although you can run `flask run` command without having to activate the `venv` `sit` created inside your project folder, we recommend you to activate the `venv` inside the project folder when you're developing your application.<br />
This is because when your application depends on eternal dependencies, they should be added within the `venv` **inside your project folder**.<br /> So, inside the project folder:

```sh
source venv/bin/activate
```

Then install any external dependencies using pip:

```sh
pip install package-you-need
```

And it will work on development run `flask run` and be deployed when `sit deploy`.

### Working with your old projects

`sit` can be used to deploy your old flask projects too.<br />
As long as they are packed in a package, you can `sit init` and then `sit deploy`.


## License

Sit is open source software [licensed as MIT]()
