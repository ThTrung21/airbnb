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
import Input from "../components/inputs/Input";

import getPostSearchResults from "../actions/getPostSearchResults";

interface ExploreClientProps {
  posts: Post[];
  currentUser: SafeUser | null;
}
const ExploreClient: React.FC<ExploreClientProps> = ({
  posts,
  currentUser,
}) => {
  const ogPostList = posts;

  let disabled = false;
  if (!currentUser) {
    disabled = true;
  }

  const [searchQuery, setSearchQuery] = useState("");
  const [shownpost, setShownPost] = useState(posts);
  const postModal = usePostModal();

  const [isLoading, setIsLoading] = useState(false);

  const onSubmitKeyword = async () => {
    setIsLoading(true);
    try {
      if (!searchQuery) {
        // If search query is empty, reset posts to original
        setShownPost(posts);
      } else {
        const response = await axios.get("/api/searchposts", {
          params: { query: searchQuery },
        });
        setShownPost(response.data);
        console.log(shownpost);
      }
    } catch (error) {
      console.error("Error fetching posts", error);
    } finally {
      setIsLoading(false); // End the loading state
    }
  };

  const onPost = useCallback(() => {
    postModal.onOpen();
  }, [postModal]);

  return (
    <Container>
      <div className="grid grid-cols-5">
        <div className="col-start-1 col-span-1">
          <Button disabled={disabled} label="Add new post" onClick={onPost} />
        </div>
        <div className="col-start-2 col-span-4">
          <input
            placeholder="Search a tour..."
            className="
                peer
                w-full
                py-3
                p-4
                ml-4
                font-light
                bg-white
                border-2
                rounded-ld
                outline-none
                transition
                pl-4
                text-md
                border-neutral-300
                focus:border-neutral-500
                "
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)} // Update searchQuery on change
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSubmitKeyword(); // Trigger search when Enter is pressed
              }
            }}
          ></input>
        </div>
      </div>

      {/* post list */}
      <div className=" mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-4 gap-8 ">
        {shownpost.map((post) => {
          return (
            <Postingcard currentUser={currentUser} key={post.id} data={post} />
          );
        })}
      </div>
    </Container>
  );
};

export default ExploreClient;
