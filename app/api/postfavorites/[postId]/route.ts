import { NextResponse } from "next/server";
import getCurrentUser from "@/app/actions/getCurrentUser";
import prisma from "@/app/libs/prismadb";
import getPosts from "@/app/actions/getPosts";
import getPostById from "@/app/actions/getPostById";

interface IParams {
  postId: string;
}

export async function POST(request: Request, { params }: { params: IParams }) {
  const currentUser = await getCurrentUser();
  if (!currentUser) {
    return NextResponse.error();
  }
  const { postId } = params;
  if (!postId || typeof postId != "string") {
    throw new Error("Invalid ID");
  }

  let postLikeIds = [...(currentUser.postLikeIds || [])];
  // push to var arr
  postLikeIds.push(postId);

  //update user and post
  // const user = await prisma.user.update({
  //   where: {
  //     id: currentUser.id,
  //   },
  //   data: {
  //     postLikeIds: postLikeIds,
  //   },
  // });

  const [user, post] = await prisma.$transaction([
    prisma.user.update({
      where: {
        id: currentUser.id,
      },
      data: {
        postLikeIds: postLikeIds,
      },
    }),
    prisma.post.update({
      where: {
        id: postId,
      },
      data: {
        likeNum: {
          increment: 1, // Increment the like count by 1
        },
        LikeIds: {
          push: currentUser.id, // Use Prisma's `push` operator to add the new ID
        },
      },
    }),
  ]);

  return NextResponse.json({ user, post });

  return NextResponse.json(user);
}

export async function DELETE(
  request: Request,
  { params }: { params: IParams }
) {
  const currentUser = await getCurrentUser();

  if (!currentUser) {
    return NextResponse.error();
  }
  const { postId } = params;
  const currentPost = await getPostById({ postId });
  if (!postId || typeof postId != "string") {
    throw new Error("Invalid ID");
  }

  let postLikeIds = [...(currentUser.postLikeIds || [])];
  let postLikeArr = [...(currentPost?.LikeIds || [])];
  postLikeIds = postLikeIds.filter((id) => id != postId);
  postLikeArr = postLikeArr.filter((id) => id != currentUser.id);
  const [user, post] = await prisma.$transaction([
    prisma.user.update({
      where: {
        id: currentUser.id,
      },
      data: {
        postLikeIds: postLikeIds,
      },
    }),
    prisma.post.update({
      where: {
        id: postId,
      },
      data: {
        LikeIds: postLikeArr,
        likeNum: {
          decrement: 1,
        },
      },
    }),
  ]);
  return NextResponse.json(user);
}
