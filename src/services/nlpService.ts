import { Movie } from '../models/movie';

export class NLPService {
    private movies: Movie[];

    constructor(movies: Movie[]) {
        this.movies = movies;
    }

    public processKeywords(keywords: string): string[] {
        // Simple keyword processing: split by spaces and return unique keywords
        return [...new Set(keywords.toLowerCase().split(' '))];
    }

    public getSimilarMovies(keywords: string): Movie[] {
        const processedKeywords = this.processKeywords(keywords);
        return this.movies.filter(movie => 
            processedKeywords.some(keyword => 
                movie.title.toLowerCase().includes(keyword) || 
                movie.description.toLowerCase().includes(keyword)
            )
        );
    }
}