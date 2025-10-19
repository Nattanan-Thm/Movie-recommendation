export class Movie {
    title: string;
    genre: string;
    description: string;
    rating: number;

    constructor(title: string, genre: string, description: string, rating: number) {
        this.title = title;
        this.genre = genre;
        this.description = description;
        this.rating = rating;
    }
}