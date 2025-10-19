# Movie Recommendation App

This is a web application that provides movie recommendations based on keywords entered by the user. It utilizes Natural Language Processing (NLP) techniques to analyze user input and suggest similar movies from a dataset.

## Features

- Enter keywords related to movie preferences.
- Get personalized movie recommendations.
- Built with TypeScript and Express for the backend.
- Simple HTML frontend for user interaction.

## Project Structure

```
movie-recommendation-app
├── src
│   ├── app.ts
│   ├── controllers
│   │   └── recommendationController.ts
│   ├── routes
│   │   └── recommendationRoutes.ts
│   ├── services
│   │   └── nlpService.ts
│   ├── models
│   │   └── movie.ts
│   ├── types
│   │   └── index.ts
│   └── utils
│       └── helpers.ts
├── public
│   └── index.html
├── package.json
├── tsconfig.json
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd movie-recommendation-app
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Running the Application

To run the backend server, execute the following command:
```
npm start
```

Open `public/index.html` in your web browser to access the frontend.

## Usage

1. Enter keywords related to the movies you are interested in.
2. Click the search button to get recommendations.
3. View the recommended movies displayed on the page.

## Technologies Used

- TypeScript
- Express.js
- Natural Language Processing Libraries
- HTML/CSS for frontend

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.