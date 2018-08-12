This project was bootstrapped with [`Sit`](https://github.com/Jinsung-L/sit/).

You can find some help and guide at [here](https://github.com/Jinsung-L/sit/)

# Server configurations

## Supervisor

`Sit` uses [Supervisor](http://supervisord.org) to manage the lifecycle of deployed applications.
And you can manually configure its settings via `/etc/supervisor/supervisord.conf`. Or you can find different locations for the configuration file depending on your OS at [here](http://supervisord.org/configuration.html).

### Enable Supervisor Web Console

`Supervisor` provides web interface for checking & managing its programs, but you have to enable it first.

Open your `supervisord.conf` and add theses lines:

```ini
[inet_http_server]
port = YOUR_SERVERS_IP_ADDRESS:9001
username = ADMIN_USERNAME
password = ADMIN_PASSWORD
```

Pick right values for `YOUR_SERVERS_IP_ADDRESS`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` respectively, and then save the file, restart the `Supervisor`.

```sh
sudo supervisorctl reread
sudo service supervisor restart
```

Open `http://YOUR_SERVERS_IP_ADDRESS:9001` in your browser and login.<br />
You'll see your deployed applications in the list.

You can find more information about it from [here](http://supervisord.org/configuration.html#inet-http-server-section-settings)
