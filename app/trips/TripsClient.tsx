"use client";
import Container from "../components/Container";
import { SafeReservation, SafeUser } from "../types";
import Heading from "../components/Heading";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import ListingCard from "../components/listings/ListingCard";

interface TripsClientProps {
  reservations: SafeReservation[];
  currentUser: SafeUser | null;
}

const TripsClient: React.FC<TripsClientProps> = ({
  reservations,
  currentUser,
}) => {
  const router = useRouter();
  const [deletingId, setDeletingId] = useState("");

  const onCancel = useCallback(
    (id: string) => {
      setDeletingId(id);

      axios
        .delete(`/api/reservations/${id}`)
        .then(() => {
          toast.success("Reservation canceled");
          router.refresh();
        })
        .catch((error) => {
          toast.error(error?.response?.data?.error);
        })
        .finally(() => {
          setDeletingId("");
        });
    },
    [router]
  );

  return (
    <Container>
      <Heading
        title="Trips"
        subtitle="Where you've been and where you're going"
      />
      <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-8">
        {reservations.map((reservation) => {
          const reservationDate = new Date(reservation.startDate); // Convert the string to a Date object
          const isPastDate = new Date() >= reservationDate; // Check if the current datetime is on or after the reservation start date
          const isDisabled = deletingId === reservation.id || isPastDate; // Determine if the card should be disabled
          const actionLabel = isDisabled
            ? "Cannot cancel"
            : "Cancel reservation"; // Set actionLabel dynamically

          return (
            <ListingCard
              key={reservation.id}
              data={reservation.listing}
              reservation={reservation}
              actionId={reservation.id}
              onAction={onCancel}
              disabled={isDisabled}
              actionLabel={actionLabel}
              currentUser={currentUser}
            />
          );
        })}
      </div>
    </Container>
  );
};
export default TripsClient;
