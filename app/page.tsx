import Container from "./components/Container";
import ClientOnly from "./components/ClientOnly";
import EmptyState from "./components/EmptyState";
import getListings, { IListingsParams } from "./actions/getListings";
import ListingCard from "./components/listings/ListingCard";
import getCurrentUser from "./actions/getCurrentUser";
import getRecommendations from "./actions/getRecommendations";
import axios from "axios";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { SafeListing } from "./types";
import { Listing } from "@prisma/client";

interface HomeProps {
  searchParams: IListingsParams;
}

const Home = async ({ searchParams }: HomeProps) => {
  const currentUser = await getCurrentUser();
  const isRecommendation = searchParams?.recommendation === "true";

  //user logged in
  let listings;
  if (isRecommendation) {
    if (currentUser == null) {
      listings = await getListings(searchParams);
    } else {
      const response = await axios.get<SafeListing[]>(
        "http://localhost:3000/api/recommendation",
        {
          params: { userId: currentUser.id.toString() },
        }
      );
      listings = await response.data;
    }
  } else {
    listings = await getListings(searchParams);
  }

  if (listings.length === 0) {
    return (
      <ClientOnly>
        <EmptyState showReset />
      </ClientOnly>
    );
  }

  return (
    <ClientOnly>
      <Container>
        <div
          className=" 
        pt-24
        grid
        grid-cols-1
        sm:grid-cols-2
        md:grid-cols-3
        lg:grid-cols-4
        xl:grid-cols-5
        2xl:grid-cols-6
        gap-8"
        >
          {listings.map((listing) => {
            return (
              <ListingCard
                currentUser={currentUser}
                key={listing.id}
                data={listing}
              />
            );
          })}
        </div>
      </Container>
    </ClientOnly>
  );
};
export default Home;
