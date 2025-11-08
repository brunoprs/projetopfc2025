import { useState, useRef, useEffect } from "react";
import { Send, MessageCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import api from "@/services/api";

export default function ChatBot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { from: "bot", text: "Olá 👋! Eu sou o assistente da PiFloor. Como posso te ajudar hoje?" },
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);


    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = { from: "user", text: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await api.chatService.sendMessage(userMessage.text);

            const botResponse = {
                from: "bot",
                text: response.reply || "Desculpe, tive um problema para responder."
            };
            setMessages((prev) => [...prev, botResponse]);

        } catch (error) {
            console.error("Erro ao enviar mensagem:", error);
            const errorResponse = {
                from: "bot",
                text: "Desculpe, estou com problemas de conexão. Tente novamente."
            };
            setMessages((prev) => [...prev, errorResponse]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="fixed bottom-6 right-6 z-50">
                {!isOpen && (
                    <button
                        onClick={() => setIsOpen(true)}
                        className="bg-secondary hover:bg-primary/90 text-primary-foreground rounded-full p-4 shadow-lg transition-all"
                    >
                        <MessageCircle className="h-8 w-8" />
                    </button>
                )}
            </div>

            {isOpen && (
                <div className="fixed bottom-6 right-6 w-80 md:w-96 bg-white border border-gray-200 shadow-2xl rounded-2xl flex flex-col overflow-hidden z-50 max-h-[70vh]">
                    <div className="bg-primary text-primary-foreground flex justify-between items-center px-4 py-3">
                        <div className="font-semibold">Assistente PiFloor 🤖</div>
                        <button onClick={() => setIsOpen(false)} className="hover:text-gray-200">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex ${msg.from === "user" ? "justify-end" : "justify-start"}`}
                            >
                                <div
                                    className={`max-w-[75%] p-3 rounded-xl text-sm shadow-sm ${msg.from === "user"
                                        ? "bg-primary text-primary-foreground"
                                        : "bg-white text-gray-800 border border-gray-200"
                                        }`}
                                >
                                    {msg.text}
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="p-3 rounded-xl text-sm bg-white text-gray-800 border border-gray-200">
                                    <div className="flex items-center space-x-1">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    <div className="flex items-center border-t border-gray-200 p-2 bg-white">
                        <input
                            type="text"
                            placeholder="Digite sua mensagem..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSend()}
                            className="flex-1 border-none outline-none text-sm p-2 bg-transparent"
                            disabled={isLoading}
                        />
                        <Button size="icon" variant="ghost" onClick={handleSend} disabled={isLoading}>
                            <Send className="h-5 w-5 text-primary" />
                        </Button>
                    </div>
                </div>
            )}
        </>
    );
}