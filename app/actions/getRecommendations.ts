import prisma from "@/app/libs/prismadb";
import { Listing } from "@prisma/client";
import axios from "axios";
import { useRouter } from "next/navigation";
import { SafeListing } from "../types";

export interface IRecommendationParams {
  userId: string | null;
}
export default async function getRecommendations(
  params: string
): Promise<SafeListing[]> {
  try {
    const userId = params;

    if (!userId) {
      return []; // or handle redirect if used inside a route handler
    }
    console.log("Attempting to talk to api...");
    // Call Flask recommendation API
    const apiResponse = await axios.get("/api/recommendation", {
      params: { query: userId },
    });

    const rankedListings = apiResponse.data.ranked_listings;
    if (!Array.isArray(rankedListings) || rankedListings.length === 0) {
      return [];
    }

    // Extract listing IDs in ranked order
    const listingIds: string[] = rankedListings.map(
      (item: { listing_id: string }) => item.listing_id
    );

    // Query listings from the database
    const listings = await prisma.listing.findMany({
      where: {
        id: {
          in: listingIds,
        },
      },
    });

    // Reorder listings to match ranking
    let orderedListings = listingIds
      .map((id) => listings.find((listing) => listing.id === id))
      .filter(Boolean) as Listing[];

    const safeListings = orderedListings.map((listing) => ({
      ...listing,
      createdAt: listing.createdAt.toISOString(),
    }));

    return safeListings;
  } catch (error: any) {
    console.error("Error in getRecommendations:", error);
    throw new Error("Failed to fetch recommendations.");
  }
}
