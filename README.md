
![Captura de pantalla 2023-12-22 a la(s) 7 45 45 p m](https://github.com/vnponce/shorten/assets/11002279/efcc6803-b1c6-433b-afa6-033d885c5b3d)


### Shorten - FastAPI URL shortener app

## About The Project

### Shorten

An API used to shorten long URLs.

#### How it Works

When submitting a URL, MD5 string is generated and added to an SQLite database with the submitted corresponding URL.  
The user is then given a short URL formatted like so: https://s.com/short_code, the `short_code` being the hashed
string.   
Whenever this unique URL is visited, the user will get the corresponding URL in the database.

#### Decisions

##### Why MD5
It was easier to implement than create another function that returns a hash and less prone to collisions.
Also if the code found a collision the long hash string (32 chars) helps to implement logic to use the other rest of characters to avoid collisions.
The way the logic solve it is moving one space at a time when it finds the `short_code` (7 chars) that were already stored in the database related to another URL

##### Lib module
Here we can find the `genereate_url` method to make the code easier to read and scalable to be used or implemented in other places

##### Url Class (generate unique short code)
Trying to do my best in Python and my knowledge of OOP from others languages (like, PHP and Ruby) I decided to move part of the code related to the URL model to its own model file.

The `@classmethod` decision.
It is wise to take this code from the `route` file to another place and keep it clean and readable, that is the main reason to don't let `route` files know how to `generate the unique short code`, this should be one URL specific task.
```python
    @classmethod
    async def generate_unique_short_code(cls, url: str):
        md5_for_url = generate_url(url, size=32)
        short_code = md5_for_url[:DEFAULT_SHORT_CODE_LENGTH]
        starting_index = 1
    
        while True:
            query = url_table.select().where(url_table.c.short_code == short_code)
            record = await database.fetch_one(query)
            if record is None:
                break
            short_code = traverse_md5(starting_index, md5_for_url)
    
        return short_code
```

As you can see the method `move_one_place_to_the_right` is agnostic and lives in the `libs` folder to be reusable from any other place in the code.

##### Url Class (computed prop)
First of all the database only stores the url and short_code properties, this is intentional because with this decision we can change the main domain and keep the logic without any major changes.
Knowing that, the way (and repeat my self) I try to implement my best OOP knowledge was creating a "computed" method how it is called in the "pydantic" world to return back the correct `domain` plus the specific `short_code`
```python
    @computed_field
    @property
    def short_url(self) -> str:
        return "https://s.com/" + self.short_code
```

##### Url Class (validation)
Implementing `AnyUrl` was not as simple as I expected, maybe there is a easy way, but I found a caveat. The `AnyUrl` from _pydantic_ returns a _pydantic object_ instead of a string, the database is expecting a `string` to be stored in the `url` column.
Looking around the web I found this discussion called ["How can I integrate pydantic v2 URLs in code?"](https://github.com/pydantic/pydantic/discussions/6395)  taking the [Annotated Validator way](https://github.com/pydantic/pydantic/discussions/6395#discussioncomment-7159870)
It a simple hack where we can convert the `AnyUrl` object to a `string` by a `lambda` function, all of this after the validation was passed.
```python
UrlString = Annotated[AnyUrl, AfterValidator(lambda v: str(v))]


class UrlIn(BaseModel):
    url: UrlString
```

##### Url Class (handle db calls)
Since the router only has one responsibility I implemented the Dependency Injection provided by FastApi to make it more readable and maintainable, sending all the DB calls code to Url Class, where it belongs.

Like:
```python

async def by_shortcode(cls, short_code: str):
    pass

async def by_url(cls, url: str):
    pass

async def find_or_create(cls, url_in: UrlIn):
    pass
```
##### Why 7 chars
To ensure project scalability rather than 7 chars bring the possibilities to create around 3,500 Billions Urls. MD5 has a 62 chars dictionary giving us the potential of 62 power 7 (62^7) records

##### TDD
As you can see in the commits, all the project development was driven by testing. This is **the way I use to work** and I fell so comfortable implementing TDD in all my projects since 2015.
I've noticed that following TDD as developers we improve communication and collaboration thus we share and ask better questions to understand the task and the business logic, also I know this help to detect early bugs that we can catch and fix before making potential damage.
**Also, you can notice, from _refactor_ commits that I did great refactors with 100% confidence thus the tests told me everything it was working correctly.**


##### SqLite
It was the easiest SQL database to configure. It is also fast to create a POC

#### Built With

* [FastAPI](https://fastapi.tiangolo.com/)
* [Pydantic](https://docs.pydantic.dev/latest/)
* [Pytest](https://docs.pytest.org/en/7.4.x/)
* [SqlAlchemy](https://www.sqlalchemy.org/)
* Sqlite
* ♥️

## Run Locally

Clone using

    $ git clone https://github.com/vnponce/shorten 

Create a virtual environment for the project and activate it:

    $ virtualenv venv
    $ source venv/bin/activate

Install the required packages:

    $ pip install -r requirements.txt

Run the app using:

    $ python -m uvicorn main:app

Access the docs in browser: http://127.0.0.1:8000/docs

## Improvements
- ~~Validate the data input is a correct URL~~
- AWS Lambdas
- More advance Python patterns, I'd like to learn more about them.
- Remove URL's longer than 30 days
