
![Logo](https://mychessrepertoire.com/logo.svg)


# My Chess Repertoire

https://mychessrepertoire.com is the best tool for chess players to store and view their opening repertoire.
In this repository you will find the code for the backend of the application. It is an API that creates the repertoire and much more!


## Features

- Get a generated opening repertoire for your playing style.
- No need to manually build your repertoire with hundreds of lines.
- Customizable.
- Free


## FAQ


Please visit https://mychessrepertoire.com/faq if you have any questions, or you can also reach out to me to brea.emanuel@gmail.com



## Run Locally

Clone the project

```bash
  git clone https://github.com/emanuelbrea/chess-opening-generator
```

Go to the project directory

```bash
  cd my-chess-repertoire
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python .\application.py
```


## Tech Stack

**Client:** React, Material UI

**Server:** Python, Flask

**Database:** Postgresql

**Library:** https://pypi.org/project/chess/ for chess logic
## API Reference
https://documenter.getpostman.com/view/14469653/2s83zgvR3D
#### Create an opening repertoire

```http
  POST /api/repertoire
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `color` | `string` | **Required**. White or black |

#### Get user repertoire

```http
  GET /api/repertoire/${fen}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `fen`      | `string` | **Required**. FEN of the position |


#### Get stats of a position
```http
  GET /api/position/stats/${fen}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `fen`      | `string` | **Required**. FEN of the position |

#### And many more..
## Contributing

Contributions are always welcome!

See `contributing.md` for ways to get started.

Please adhere to this project's `code of conduct`.


## Feedback

If you have any feedback, please reach out to me at brea.emanuel@gmail.com


## License


[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

## Authors

- [@emanuelbrea](https://www.github.com/emanuelbrea)

