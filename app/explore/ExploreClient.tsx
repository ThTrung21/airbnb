"use client";
import Container from "../components/Container";
import { SafeListing, SafeUser } from "../types";
import Heading from "../components/Heading";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import ListingCard from "../components/listings/ListingCard";
import getListingById from "../actions/getListingById";
import { Post } from "@prisma/client";
import usePostModal from "../hooks/usePostModal";
import Button from "../components/Button";
import Postingcard from "../components/posting/PostingCard";
import usePostInfoModal from "../hooks/usePostInfoModal";

interface ExploreClientProps {
  posts: Post[];
  currentUser: SafeUser | null;
}
const ExploreClient: React.FC<ExploreClientProps> = ({
  posts,
  currentUser,
}) => {
  let disabled = false;
  if (!currentUser) {
    disabled = true;
  }
  const postModal = usePostModal();

  const onPost = useCallback(() => {
    postModal.onOpen();
  }, [postModal]);

  return (
    <Container>
      <div className="grid grid-cols-5">
        <div className="col-start-3 col-span-1">
          <Button disabled={disabled} label="Add new post" onClick={onPost} />
        </div>
      </div>
      {/* post list */}
      <div className=" mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-4 gap-8 border border-red-800">
        {posts.map((post) => {
          return (
            <Postingcard currentUser={currentUser} key={post.id} data={post} />
          );
        })}
      </div>
    </Container>
  );
};

export default ExploreClient;
