"use client";
import { useMemo, useState } from "react";
import useRentModal from "../../hooks/useRentModal";
import Modal from "./Modal";
import Heading from "../Heading";

import {
  Field,
  FieldValue,
  FieldValues,
  SubmitHandler,
  useForm,
} from "react-hook-form";
import CountrySelect from "../inputs/CountrySelect";
import dynamic from "next/dynamic";
import Counter from "../inputs/Counter";
import ImageUpload from "../inputs/ImageUpload";
import Input from "../inputs/Input";
import axios from "axios";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";
import usePostModal from "@/app/hooks/usePostModal";
import TextArea from "../inputs/TextArea";

const PostModal = () => {
  const router = useRouter();
  const postModal = usePostModal();

  const [isLoading, setIsLoading] = useState(false);
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    reset,
  } = useForm<FieldValues>({
    defaultValues: {
      imageSrc: "",
      title: "",
      description: "",
    },
  });

  const imageSrc = watch("imageSrc");

  console.log(imageSrc);

  const setCustomValue = (id: string, value: any) => {
    setValue(id, value, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    });
  };

  const onSubmit: SubmitHandler<FieldValues> = (data) => {
    setIsLoading(true);

    axios
      .post("/api/explore", data)
      .then(() => {
        toast.success("listing Created!");
        router.refresh();
        reset();

        postModal.onClose();
      })
      .catch(() => {
        toast.error("Something went wrong");
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const bodyContent = (
    <div className="flex flex-col gap-8">
      <Heading title="Title" />
      <Input
        id="title"
        label="Title"
        disabled={isLoading}
        register={register}
        errors={errors}
        required
      />

      <Heading title="Description" />
      <TextArea
        id="description"
        label="Description"
        disabled={isLoading}
        register={register}
        errors={errors}
        required
      />
      <Heading title="Add a photo to your post" />
      <ImageUpload
        value={imageSrc}
        onChange={(value) => setCustomValue("imageSrc", value)}
      />
    </div>
  );

  return (
    <Modal
      isOpen={postModal.isOpen}
      title="New Post"
      onClose={postModal.onClose}
      onSubmit={handleSubmit(onSubmit)}
      actionLabel="Create post"
      body={bodyContent}
    ></Modal>
  );
};

export default PostModal;
