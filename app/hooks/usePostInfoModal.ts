import { create } from "zustand";
import { Post } from "@prisma/client";

interface PostInfoModalStore {
  isOpen: boolean;
  post: Post | null;
  onOpen: (post: Post) => void;
  onClose: () => void;
}

const usePostInfoModal = create<PostInfoModalStore>((set) => ({
  isOpen: false,
  post: null,
  onOpen: (post: Post) => set({ isOpen: true, post }), // Store the Post object
  onClose: () => set({ isOpen: false, post: null }),
}));

export default usePostInfoModal;
