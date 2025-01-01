import prisma from "@/app/libs/prismadb";
import axios from "axios";

export interface IPostParams {
  userId?: string;
  searchQuery?: string;
}

export default async function getPostSearchResults(params: IPostParams) {
  try {
    const { searchQuery } = params;
    if (!searchQuery) {
      throw new Error("Search query is required");
    }
    // call api
    const apiResponse = await axios.get("http://127.0.0.1:5000/search", {
      params: { query: searchQuery },
    });
    // re-objecid the stringified objectid array
    const objectIds: string[] = apiResponse.data;
    if (!Array.isArray(objectIds) || objectIds.length === 0) {
      return []; // Return an empty array if no results
    }

    // Query all posts with the matching IDs
    const posts = await prisma.post.findMany({
      where: {
        id: {
          in: objectIds,
        },
      },
    });
    const orderedPosts = objectIds
      .map((id) => posts.find((post) => post.id === id))
      .filter(Boolean);
    return orderedPosts;
  } catch (error: any) {
    throw new Error(error);
  }
}
