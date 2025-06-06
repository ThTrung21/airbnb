import prisma from "@/app/libs/prismadb";
import { NextResponse } from "next/server";
import axios from "axios";
import { Listing } from "@prisma/client";
import { SafeListing } from "@/app/types";

const RECOMMENDATION_API_URL = "http://127.0.0.1:5000/recommendation"; // Flask API endpoint

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get("userId");
  console.log("Received userId:", userId);

  try {
    // Call Flask API to get ranked listings
    const flaskResponse = await axios.get(RECOMMENDATION_API_URL, {
      params: { userId },
    });

    // Extract the listing IDs in ranked order
    const parsedData = JSON.parse(flaskResponse.data);
    const rankedListings = parsedData.ranked_listings;
    const listingIds: string[] = rankedListings.map(
      (item: { listing_id: string }) => item.listing_id
    );

    // Fetch the listings from the database
    const listings = await prisma.listing.findMany({
      where: {
        id: { in: listingIds },
      },
    });

    // Reorder the listings to match the ranking order
    const orderedListings = listingIds
      .map((id) => listings.find((listing) => listing.id === id))
      .filter(Boolean) as Listing[]; // Remove any nulls in case a listing wasn't found

    const safeListings = orderedListings.map((listing) => ({
      ...listing,
      createdAt: listing.createdAt.toISOString(),
    }));
    return NextResponse.json(safeListings);
    safeListings;
  } catch (error) {
    console.error("Error fetching ranked listings:", error);
    return NextResponse.json({});
  }
}
