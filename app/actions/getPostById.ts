import prisma from "@/app/libs/prismadb";

interface IParams {
  postId: string;
}
export default async function getPostById(params: IParams) {
  try {
    const { postId } = params;

    const post = await prisma.post.findUnique({
      where: {
        id: postId,
      },
      include: {
        user: true,
      },
    });

    if (!post) {
      return null;
    }
    return post;
  } catch (error: any) {
    throw new Error(error);
  }
}
