"use client"
import {Card, CardHeader, CardTitle, CardContent, CardFooter} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion"
import { useState } from "react";
import  Link  from "next/link"

export default function WelcomeModal(props: {isOpen: boolean}) {

    const [isOpen, setIsOpen] = useState(props.isOpen);
    const handleClose = () => {
        setIsOpen(false);
    }
    return (
        <>
        {isOpen && (
        <div className="h-screen w-screen flex flex-col items-center justify-center">
        <Card className="lg:w-[25%] w-[90%]">
            <CardHeader>
            <CardTitle className="text-4xl">Agentic Ambience</CardTitle>
            </CardHeader>
            <CardContent>
            <p className="mb-4">A transparent experiment in collective sound generation and sharing.</p>
            <Accordion type="single" collapsible>
                <AccordionItem value="item-1">
                    <AccordionTrigger>About the System</AccordionTrigger>
                    <AccordionContent>
                        <p className="mb-4">
                            Each soundscape is created from a photo. The system uses details like weather, time of day, location, and current events to generate a unique atmosphere in sound.
                        </p>
                        <p className="mb-4">
                            The project is designed to show both the possibilities and the limitations of this kind of technology. By giving feedback on the soundscapes, you help the system learn what people associate with ambience. Over time, this feedback builds a collective understanding of how ambience should feel.
                        </p>
                        <p className="mb-4">
                            Agentic Ambience is a way to explore how machines interpret the world and how people can shape that interpretation together. Let&apos;s see what happens...
                        </p>
                        <small className="text-xs">The system is built using a combination of open-source generative AI models, which will have their own biases and limitations.</small>
                    </AccordionContent>
                </AccordionItem>
            </Accordion>

            </CardContent>
        <CardFooter className="flex justify-end">
            <Link href="/generate">
                <Button onClick={handleClose} className="cursor-pointer">Start</Button>
            </Link>
        </CardFooter>
        </Card>
        
        </div>
        )}
        </>
    );
}
