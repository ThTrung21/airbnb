import Container from "../components/Container";
import ClientOnly from "../components/ClientOnly";
import EmptyState from "../components/EmptyState";
import getListings, { IPostParams } from "../actions/getPosts";
import ListingCard from "../components/listings/ListingCard";
import getCurrentUser from "../actions/getCurrentUser";
import getPosts from "../actions/getPosts";
import ExploreClient from "./ExploreClient";
import Button from "../components/Button";
import usePostModal from "../hooks/usePostModal";
import { useCallback } from "react";
import PostModal from "../components/modals/PostModal";
import PostInfoModal from "../components/modals/PostInfoModal";

const ExplorePage = async () => {
  const currentUser = await getCurrentUser();

  if (!currentUser) {
    return (
      <ClientOnly>
        <EmptyState title="Unauthorized" subtitle="Please login" />
      </ClientOnly>
    );
  }

  const posts = await getPosts({
    userId: currentUser.id,
  });

  return (
    <ClientOnly>
      <PostModal />
      <PostInfoModal />
      <ExploreClient posts={posts} currentUser={currentUser} />
    </ClientOnly>
  );
};

export default ExplorePage;
