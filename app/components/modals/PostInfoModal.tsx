"use client";
import { useMemo, useState } from "react";
import useRentModal from "../../hooks/useRentModal";
import Modal from "./Modal";
import Heading from "../Heading";
import Image from "next/image";
import { useRouter } from "next/navigation";
import usePostModal from "@/app/hooks/usePostModal";
import TextArea from "../inputs/TextArea";
import usePostInfoModal from "@/app/hooks/usePostInfoModal";
import Postingcard from "../posting/PostingCard";
import { Post } from "@prisma/client";
import getCurrentUser from "@/app/actions/getCurrentUser";
import PostHeartButton from "../PostHeartButton";

const PostInfoModal = () => {
  const router = useRouter();
  const postModal = usePostInfoModal();
  const posting = postModal.post;
  if (!posting) {
    return null;
  }
  // const currentUser = getCurrentUser();
  // console.log(imageSrc);

  const bodyContent = (
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
          src={posting.imageSrc}
          className="
          object-cover
          w-full
          h-auto
          transition"
        />
      </div>

      <div className="font-light text-neutral-500 pl-2 pr-2 max-h-[20vh] overflow-hidden">
        {posting.description}
      </div>
    </div>
  );

  return (
    <Modal
      isOpen={postModal.isOpen}
      title={posting.title}
      onSubmit={() => {}}
      onClose={postModal.onClose}
      actionLabel="Create post"
      body={bodyContent}
      isSubmitable={false}
    ></Modal>
  );
};

export default PostInfoModal;
