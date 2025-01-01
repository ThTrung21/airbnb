import prisma from "@/app/libs/prismadb";
import { NextResponse } from "next/server";
import getCurrentUser from "@/app/actions/getCurrentUser";

export async function POST(request: Request) {
  const currentUser = await getCurrentUser();

  if (!currentUser) {
    return NextResponse.error();
  }

  const body = await request.json();
  const { title, description, imageSrc } = body;

  const posts = await prisma.post.create({
    data: {
      title,
      likeNum: 0,
      description,
      imageSrc,
      userId: currentUser.id,
      LikeIds: [],
    },
  });

  return NextResponse.json(posts);
}
