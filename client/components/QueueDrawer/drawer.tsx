"use client";
import { useState } from "react";
import MatchmakingQueue from "@/components/Queue/Queue";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";

export default function QueueDrawer({
  children,
  game,
  gameData,
}: {
  children: React.ReactNode;
  game: any;
}) {
  const [open, setOpen] = useState(false);

  return (
    <Drawer
      direction="right"
      open={open}
      onOpenChange={setOpen}
      dismissible={false}
    >
      <DrawerTrigger asChild>{children}</DrawerTrigger>
      <DrawerContent className="data-[vaul-drawer-direction=right]:w-[600px] data-[vaul-drawer-direction=right]:max-w-[90vw] data-[vaul-drawer-direction=right]:sm:max-w-[600px]">
        <DrawerHeader>
          <DrawerTitle>{game.name} Queue</DrawerTitle>
          <DrawerDescription>
            Join the matchmaking queue for {game}
          </DrawerDescription>
        </DrawerHeader>
        <div
          className={
            "max-h-[calc(100vh-10rem)] overflow-y-auto max-w-[calc(100vw-10rem)]"
          }
        >
          {" "}
          <MatchmakingQueue name={game} gameId={game.id} gameData={gameData} />
        </div>
        <DrawerFooter>
          <button
            onClick={() => setOpen(false)}
            className="px-4 py-2 bg-muted rounded-lg hover:bg-muted/80 transition-colors rounded-md"
          >
            Close
          </button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
