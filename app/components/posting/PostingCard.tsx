"use client";
import { SafeListing, SafeReservation, SafeUser } from "@/app/types";
import { Listing, Post, Reservation, User } from "@prisma/client";
import { useRouter } from "next/navigation";
import React, { useCallback, useMemo } from "react";

import { format } from "date-fns";
import Image from "next/image";

import Button from "../Button";
import PostHeartButton from "../PostHeartButton";
import usePostInfoModal from "@/app/hooks/usePostInfoModal";
interface PostingCardProps {
  data: Post;

  disabled?: boolean;
  actionLabel?: string;
  actionId?: string;
  currentUser?: SafeUser | null;
}

const Postingcard: React.FC<PostingCardProps> = ({
  data,

  // onAction,
  disabled,
  actionLabel = "",
  actionId = "",
  currentUser,
}) => {
  const router = useRouter();
  const postInfoModal = usePostInfoModal();

  const onPostInfo = useCallback(() => {
    postInfoModal.onOpen(data);
  }, [postInfoModal, data]);

  return (
    <div
      onClick={onPostInfo}
      className="col-span-1 group border cursor-pointer border-neutral-800 rounded-md mb-4 shadow-lg hover:shadow-2xl transition-shadow duration-350"
    >
      <div className="flex flex-col gap-2 w-full ">
        <div
          className="
        w-full
        relative
        overflow-hidden
        rounded-xl
        h-[30vh]
        max-h-[50vh]"
        >
          <Image
            fill
            alt="post"
            src={data.imageSrc}
            className="
          object-cover
          w-full
          h-full
          transition"
          />
          <div className="absolute top-3 right-3">
            <PostHeartButton postId={data.id} currentUser={currentUser} />
          </div>
        </div>
        <div className="font-semibold text-lg pl-2 pr-2">{data.title}</div>
        <div className="font-light text-neutral-500 pl-2 pr-2 max-h-[20vh] overflow-hidden">
          {data.description}
        </div>
      </div>
    </div>
  );
};

export default Postingcard;
