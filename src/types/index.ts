export interface Movie {
    title: string;
    genre: string;
    description: string;
    rating: number;
}

export interface RecommendationRequest {
    keywords: string[];
}