export const loadDataset = async (filePath: string): Promise<any[]> => {
    const response = await fetch(filePath);
    const data = await response.json();
    return data;
};

export const formatResponse = (movies: any[]): string => {
    return movies.map(movie => `${movie.title} (${movie.year}) - ${movie.genre}`).join('\n');
};