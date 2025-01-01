import prisma from "@/app/libs/prismadb";
import { NextResponse } from "next/server";
import axios from "axios";

const SEARCH_API_URL = "http://127.0.0.1:5000/search"; // Flask API endpoint

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const searchQuery = searchParams.get("query");

  if (!searchQuery) {
    return NextResponse.json(
      { error: "Search query is required" },
      { status: 400 }
    );
  }

  try {
    // Call Flask API to get ObjectIDs
    const flaskResponse = await axios.get(SEARCH_API_URL, {
      params: { query: searchQuery },
    });

    const objectIds: string[] = flaskResponse.data; // Assuming Flask returns an array of string IDs
    console.log(objectIds);
    // Query Prisma to fetch posts with matching IDs
    const posts = await prisma.post.findMany({
      where: {
        id: { in: objectIds },
      },
    });
    const orderedPosts = objectIds
      .map((id) => posts.find((post) => post.id === id))
      .filter(Boolean);
    return NextResponse.json(orderedPosts);
  } catch (error: any) {
    console.error("Error fetching posts:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
