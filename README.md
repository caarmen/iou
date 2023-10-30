# IOU

Webapp to keep track of who owes how much to whom, amongst two people.

Each time Person A owes an amount to Person B, enter this in the app by specifying the amount, an optional description, selecting Persion A, and submitting.

At any given moment, either:
*  both Persion A and B will owe each other the same amount of money, which means the net debt is 0.
*  or the net debt will belong to one of the two. In the case of a non-zero net debt, the application shows who owes what.

The application also displays the most recent 5 debts.

## Running

### Setup the environment

Copy the `.env.template` from this project to a file `.env`, and adjust any parameters.

* The `SECRET_KEY` can be generated using the [get_random_secret_key](https://github.com/django/django/blob/5.0b1/django/core/management/utils.py#L79:L84) function in Django.
* Set `DEBUG` to `false` for a production environment.

### Run the docker image

Run the docker image, exposing two files with the `-v` volume commands:
* Your `.env` file
* The `iou.db` database file. If the database doesn't exist, create an empty one: `touch /path/to/iou.db`.

```
docker run --detach --publish 8000:8000 -v `pwd`/.env:/app/.env -v /path/to/iou.db:/tmp/iou.db ghcr.io/caarmen/iou
```

### Use the application

You can access:
* The admin interface at http://localhost:8000/admin/
* The end-user interface at http://localhost:8000/iou/

The first time the app is run, it creates a super user with username `admin` and password `defaultpassword`. You should change the password after logging in.
