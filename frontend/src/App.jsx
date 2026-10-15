import { useEffect, useRef, useState } from "react";
import "./App.css";

const API =
  import.meta.env.VITE_API_URL !== undefined
    ? import.meta.env.VITE_API_URL
    : window.location.port === "5173"
    ? "http://127.0.0.1:8001"
    : "";

// SVG Icons
const ChatIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
);

const MicIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
    <line x1="12" y1="19" x2="12" y2="23"></line>
    <line x1="8" y1="23" x2="16" y2="23"></line>
  </svg>
);

const HomeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
    <polyline points="9 22 9 12 15 12 15 22"></polyline>
  </svg>
);

const BellIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
  </svg>
);

const DocIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
  </svg>
);

const GlobeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="2" y1="12" x2="22" y2="12"></line>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
  </svg>
);

const ChartIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
  </svg>
);

const CpuIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
    <rect x="9" y="9" width="6" height="6"></rect>
    <line x1="9" y1="1" x2="9" y2="4"></line>
    <line x1="15" y1="1" x2="15" y2="4"></line>
    <line x1="9" y1="20" x2="9" y2="23"></line>
    <line x1="15" y1="20" x2="15" y2="23"></line>
    <line x1="20" y1="9" x2="23" y2="9"></line>
    <line x1="20" y1="14" x2="23" y2="14"></line>
    <line x1="1" y1="9" x2="4" y2="9"></line>
    <line x1="1" y1="14" x2="4" y2="14"></line>
  </svg>
);

const CalendarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
    <line x1="16" y1="2" x2="16" y2="6"></line>
    <line x1="8" y1="2" x2="8" y2="6"></line>
    <line x1="3" y1="10" x2="21" y2="10"></line>
  </svg>
);

const MailIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
    <polyline points="22,6 12,13 2,6"></polyline>
  </svg>
);

const WorkflowIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7"></rect>
    <rect x="14" y="3" width="7" height="7"></rect>
    <rect x="14" y="14" width="7" height="7"></rect>
    <rect x="3" y="14" width="7" height="7"></rect>
  </svg>
);

const TrashIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
  </svg>
);

const PaperclipIcon = () => (
  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
  </svg>
);

// Animated Fluid Organic Vortex Waveform
function FluidVortex({ isActive, size = 320 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;
    let time = 0;

    const render = () => {
      time += isActive ? 0.045 : 0.016;
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);

      const centerX = width / 2;
      const centerY = height / 2;
      const rings = 14;

      for (let r = 0; r < rings; r++) {
        ctx.beginPath();
        const baseRadius = size * 0.16 + r * (size * 0.02);
        const points = 90;
        const colorOffset = (r / rings + time * 0.22) % 1;
        const hue = 180 + colorOffset * 140;

        ctx.strokeStyle = `hsla(${hue}, 92%, ${isActive ? 68 : 55}%, ${0.25 + (r / rings) * 0.55})`;
        ctx.lineWidth = isActive ? 2.4 : 1.6;

        for (let i = 0; i <= points; i++) {
          const theta = (i / points) * Math.PI * 2;
          const waveFreq = 5 + (r % 3);
          const waveAmp = (isActive ? 22 : 9) * Math.sin(theta * waveFreq + time * 2.2 + r * 0.6);
          const rad = baseRadius + waveAmp;
          const x = centerX + Math.cos(theta + time * (r % 2 === 0 ? 0.4 : -0.4)) * rad;
          const y = centerY + Math.sin(theta + time * (r % 2 === 0 ? 0.4 : -0.4)) * (rad * 0.88);

          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.stroke();
      }

      // Central dark glowing portal
      const coreRadius = size * 0.16;
      const coreGradient = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, coreRadius);
      coreGradient.addColorStop(0, "rgba(7, 3, 16, 0.98)");
      coreGradient.addColorStop(0.7, "rgba(28, 10, 54, 0.92)");
      coreGradient.addColorStop(1, "rgba(110, 40, 200, 0.2)");
      ctx.fillStyle = coreGradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
      ctx.fill();

      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [isActive, size]);

  return <canvas ref={canvasRef} width={size} height={size} className="fluid-canvas" />;
}

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard"); // 'dashboard' | 'chat' | 'voice' | 'agenda' | 'workflows'
  const [messages, setMessages] = useState([]);
  const [historyList, setHistoryList] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [todos, setTodos] = useState([]);
  const [events, setEvents] = useState([]);
  const [systemStats, setSystemStats] = useState({ cpu_percent: 0, ram_percent: 0, ram_used_gb: 0, ram_total_gb: 0 });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState("Connecting to Echo Mind...");
  const [voiceStatus, setVoiceStatus] = useState("Tap mic to speak with Echo Mind");
  const [lastSpeech, setLastSpeech] = useState();

  // Gmail Copilot State
  const [gmailStatus, setGmailStatus] = useState({ configured: false, email: "", connected: false, message: "" });
  const [gmailMessages, setGmailMessages] = useState([]);
  const [gmailLoading, setGmailLoading] = useState(false);
  const [gmailEmailInput, setGmailEmailInput] = useState("");
  const [gmailPasswordInput, setGmailPasswordInput] = useState("");
  const [gmailConfigStatus, setGmailConfigStatus] = useState("");
  const [showConnectCard, setShowConnectCard] = useState(false);
  const [connectCardDismissed, setConnectCardDismissed] = useState(false);
  const [hideConnectedCard, setHideConnectedCard] = useState(false);
  const [draftRecipient, setDraftRecipient] = useState("");
  const [draftSubject, setDraftSubject] = useState("");
  const [draftBody, setDraftBody] = useState("");
  const [draftResult, setDraftResult] = useState("");
  const [draftLoading, setDraftLoading] = useState(false);
  // User Name State
  const [userName, setUserName] = useState("User");
  const [editingName, setEditingName] = useState(false);
  const [tempName, setTempName] = useState("");

  // Task Creation & Notifications State
  const [newTodoTitle, setNewTodoTitle] = useState("");
  const [newTodoDueDate, setNewTodoDueDate] = useState("");
  const [showNewTodoForm, setShowNewTodoForm] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const notifiedTasksRef = useRef(new Set());

  // Event Creation State
  const [newEventTitle, setNewEventTitle] = useState("");
  const [newEventDate, setNewEventDate] = useState("");
  const [newEventTime, setNewEventTime] = useState("");
  const [showNewEventForm, setShowNewEventForm] = useState(false);

  // File Attachment State (like ChatGPT)
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const fileInputRef = useRef(null);

  // Notification Center Dropdown State
  const [showNotificationsDropdown, setShowNotificationsDropdown] = useState(false);
  const notifDropdownRef = useRef(null);

  const bottomRef = useRef(null);

  // Request native Windows/browser notification permissions on first load
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
  }, []);

  // Close notifications dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (notifDropdownRef.current && !notifDropdownRef.current.contains(e.target)) {
        setShowNotificationsDropdown(false);
      }
    };
    if (showNotificationsDropdown) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showNotificationsDropdown]);

  const playNotificationSound = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(587.33, ctx.currentTime);
      osc.frequency.setValueAtTime(880, ctx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch {}
  };

  // Check upcoming tasks approaching due time (within 30 minutes)
  useEffect(() => {
    if (!Array.isArray(todos) || todos.length === 0) return;

    const checkDueTasks = () => {
      const now = new Date();
      todos.forEach((task) => {
        if (task.status === "completed" || !task.due_date) return;

        let dueDateObj = null;
        const raw = String(task.due_date).trim();

        // 1. Try ISO or standard Date parse
        const parsed = new Date(raw.replace(" ", "T"));
        if (!isNaN(parsed.getTime())) {
          dueDateObj = parsed;
        } else {
          // 2. Try time like "14:30" or "2:30 PM"
          const timeMatch = raw.match(/^(\d{1,2}):(\d{2})\s*(am|pm)?$/i);
          if (timeMatch) {
            let hrs = parseInt(timeMatch[1], 10);
            const mins = parseInt(timeMatch[2], 10);
            const meridiem = (timeMatch[3] || "").toLowerCase();
            if (meridiem === "pm" && hrs < 12) hrs += 12;
            if (meridiem === "am" && hrs === 12) hrs = 0;
            dueDateObj = new Date();
            dueDateObj.setHours(hrs, mins, 0, 0);
          }
        }

        if (!dueDateObj) return;

        const diffMinutes = (dueDateObj.getTime() - now.getTime()) / 60000;

        // Alert if due in <= 30 minutes and not overdue by more than 2 hours
        if (diffMinutes <= 30 && diffMinutes >= -120) {
          const alertKey = `${task.id}-${task.due_date}`;
          if (!notifiedTasksRef.current.has(alertKey)) {
            notifiedTasksRef.current.add(alertKey);

            const alertText =
              diffMinutes > 0
                ? `"${task.title}" is due in ${Math.round(diffMinutes)} minutes!`
                : `"${task.title}" is due right now!`;

            // Native Windows notification
            if ("Notification" in window && Notification.permission === "granted") {
              try {
                new Notification("⏰ Echo Mind: Task Approaching!", {
                  body: alertText,
                });
              } catch {}
            }

            playNotificationSound();

            setNotifications((prev) => [
              ...prev,
              {
                id: alertKey,
                taskId: task.id,
                title: task.title,
                text: alertText,
              },
            ]);
          }
        }
      });
    };

    checkDueTasks();
    const interval = setInterval(checkDueTasks, 20000);
    return () => clearInterval(interval);
  }, [todos]);

  useEffect(() => {
    fetchHealth();
    fetchUserProfile();
    fetchHistory();
    fetchWorkflows();
    fetchTodos();
    fetchEvents();
    fetchSystem();
    fetchGmailStatus();

    const interval = setInterval(fetchSystem, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchUserProfile = () => {
    fetch(`${API}/user/profile`)
      .then((r) => r.json())
      .then((d) => {
        if (d.name) {
          setUserName(d.name);
          setTempName(d.name);
        }
      })
      .catch(() => {});
  };

  const saveUserName = (newName) => {
    const trimmed = (newName || "").trim();
    if (!trimmed) {
      setEditingName(false);
      return;
    }
    setUserName(trimmed);
    setEditingName(false);
    fetch(`${API}/user/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: trimmed }),
    }).catch(() => {});
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const fetchHealth = () => {
    fetch(`${API}/health`)
      .then((r) => {
        if (!r.ok) throw new Error("Health check failed");
        return r.json();
      })
      .then((d) => setProvider(d.provider || "Echo Mind Active"))
      .catch(() => setProvider("Backend Offline — Start: python api/server.py"));
  };

  const fetchGmailStatus = () => {
    fetch(`${API}/gmail/status`)
      .then((r) => r.json())
      .then((d) => {
        setGmailStatus(d);
        if (d.email) setGmailEmailInput(d.email);
      })
      .catch(() => {});
  };

  const fetchGmailMessages = () => {
    setGmailLoading(true);
    fetch(`${API}/gmail/messages?limit=8`)
      .then((r) => r.json())
      .then((d) => {
        if (d.status === "success" && d.messages) {
          setGmailMessages(d.messages);
        }
      })
      .catch(() => {})
      .finally(() => setGmailLoading(false));
  };

  const saveGmailConfig = (e) => {
    e.preventDefault();
    if (!gmailEmailInput.trim() || !gmailPasswordInput.trim()) {
      setGmailConfigStatus("Please enter both email and App Password.");
      return;
    }
    setGmailConfigStatus("Verifying connection to Gmail...");
    fetch(`${API}/gmail/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gmail_address: gmailEmailInput,
        gmail_app_password: gmailPasswordInput,
      }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.success) {
          setGmailConfigStatus(" Connected successfully!");
          fetchGmailStatus();
          fetchGmailMessages();
          setTimeout(() => {
            setShowConnectCard(false);
            setConnectCardDismissed(true);
          }, 1200);
        } else {
          setGmailConfigStatus(` ${d.error || "Connection failed. Please check credentials."}`);
        }
      })
      .catch((err) => setGmailConfigStatus(` Error: ${err.message}`));
  };

  const handleDisconnectGmail = async () => {
    if (!window.confirm(`Disconnect ${gmailStatus.email || "this Gmail account"}?`)) return;
    try {
      const res = await fetch(`${API}/gmail/disconnect`, { method: "POST" });
      const d = await res.json();
      if (d.success) {
        setGmailStatus({ configured: false, email: "", connected: false, message: "" });
        setGmailEmailInput("");
        setGmailPasswordInput("");
        setGmailMessages([]);
        setGmailConfigStatus("");
        setShowConnectCard(false);
        setConnectCardDismissed(false);
      }
    } catch (err) {
      alert(`Error disconnecting: ${err.message}`);
    }
  };


  const handleCreateDraft = (e) => {
    e.preventDefault();
    if (!draftRecipient.trim() || !draftSubject.trim() || !draftBody.trim()) {
      setDraftResult(" Please fill recipient, subject, and body.");
      return;
    }
    setDraftLoading(true);
    setDraftResult("Creating draft in Gmail...");
    fetch(`${API}/gmail/draft`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipient: draftRecipient,
        subject: draftSubject,
        body: draftBody,
      }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.status === "success") {
          setDraftResult(` ${d.message}`);
          setDraftSubject("");
          setDraftBody("");
          setDraftRecipient("");
        } else {
          setDraftResult(` ${d.message}`);
        }
      })
      .catch((err) => setDraftResult(` Error: ${err.message}`))
      .finally(() => setDraftLoading(false));
  };

  const handleSendDirect = (e) => {
    e.preventDefault();
    if (!draftRecipient.trim() || !draftSubject.trim() || !draftBody.trim()) {
      setDraftResult(" Please fill recipient, subject, and body.");
      return;
    }
    if (!window.confirm(`Send email directly to ${draftRecipient}?`)) return;
    setDraftLoading(true);
    setDraftResult("Sending email via Gmail SMTP...");
    fetch(`${API}/gmail/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipient: draftRecipient,
        subject: draftSubject,
        body: draftBody,
      }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.status === "success") {
          setDraftResult(` ${d.message}`);
          setDraftSubject("");
          setDraftBody("");
          setDraftRecipient("");
        } else {
          setDraftResult(` ${d.message}`);
        }
      })
      .catch((err) => setDraftResult(` Error: ${err.message}`))
      .finally(() => setDraftLoading(false));
  };

  const fetchHistory = () => {
    fetch(`${API}/history?limit=15`)
      .then((r) => r.json())
      .then((data) => {
        if (data.history && data.history.length > 0) {
          setHistoryList(data.history);
        } else {
          setHistoryList([
            { id: 1, role: "user", content: "Analyze my Q3 sales spreadsheet and plot a bar chart", created_at: "Today", type: "chat" },
            { id: 2, role: "user", content: "Summarize this PDF contract and extract main terms", created_at: "Yesterday", type: "doc" },
            { id: 3, role: "user", content: "Check my system resources and RAM usage", created_at: "Earlier", type: "system" },
          ]);
        }
      })
      .catch(() => {});
  };

  const fetchWorkflows = () => {
    fetch(`${API}/workflows`)
      .then((r) => r.json())
      .then((d) => {
        if (d.workflows) setWorkflows(d.workflows);
      })
      .catch(() => {});
  };

  const fetchTodos = () => {
    fetch(`${API}/todos`)
      .then((r) => r.json())
      .then((d) => {
        if (d.todos) setTodos(d.todos);
      })
      .catch(() => {});
  };

  const fetchEvents = () => {
    fetch(`${API}/events`)
      .then((r) => r.json())
      .then((d) => {
        if (d.events) setEvents(d.events);
      })
      .catch(() => {});
  };

  const fetchSystem = () => {
    fetch(`${API}/system/resources`)
      .then((r) => r.json())
      .then((d) => {
        if (d.status === "success") {
          setSystemStats({
            cpu_percent: d.cpu_percent,
            ram_percent: d.ram_percent,
            ram_used_gb: d.ram_used_gb,
            ram_total_gb: d.ram_total_gb,
          });
        }
      })
      .catch(() => {});
  };

  const toggleTodo = async (id) => {
    try {
      await fetch(`${API}/todos/${id}/toggle`, { method: "POST" });
      fetchTodos();
    } catch (e) {
      console.error("Failed to toggle todo:", e);
    }
  };

  const deleteTodo = async (id, clickEvt) => {
    if (clickEvt) clickEvt.stopPropagation();
    if (id === undefined || id === null) {
      console.warn("deleteTodo called with invalid id:", id);
      return;
    }
    // Optimistic UI update
    setTodos((prev) => prev.filter((item) => item.id !== id));
    try {
      await fetch(`${API}/todos/${id}`, { method: "DELETE" });
      fetchTodos();
    } catch (err) {
      console.error("Failed to delete todo:", err);
      fetchTodos();
    }
  };

  const handleCreateNewTodo = async (e) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;
    try {
      await fetch(`${API}/todos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newTodoTitle.trim(),
          due_date: newTodoDueDate.trim(),
        }),
      });
      setNewTodoTitle("");
      setNewTodoDueDate("");
      setShowNewTodoForm(false);
      fetchTodos();
    } catch (err) {
      console.error("Failed to create todo:", err);
    }
  };

  const deleteEvent = async (id, clickEvt) => {
    if (clickEvt) clickEvt.stopPropagation();
    if (id === undefined || id === null) {
      console.warn("deleteEvent called with invalid id:", id);
      return;
    }
    // Optimistic UI update
    setEvents((prev) => prev.filter((item) => item.id !== id));
    try {
      await fetch(`${API}/events/${id}`, { method: "DELETE" });
      fetchEvents();
    } catch (err) {
      console.error("Failed to delete event:", err);
      fetchEvents();
    }
  };

  const handleCreateNewEvent = async (e) => {
    e.preventDefault();
    if (!newEventTitle.trim() || !newEventDate.trim()) return;
    try {
      await fetch(`${API}/events`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newEventTitle.trim(),
          date: newEventDate.trim(),
          time: newEventTime.trim(),
        }),
      });
      setNewEventTitle("");
      setNewEventDate("");
      setNewEventTime("");
      setShowNewEventForm(false);
      fetchEvents();
    } catch (err) {
      console.error("Failed to create event:", err);
    }
  };

  const getFileIcon = (type, filename = "") => {
    const ext = (filename.split(".").pop() || "").toLowerCase();
    if (type === "pdf" || ext === "pdf") return "📄";
    if (type === "docx" || ext === "docx" || ext === "doc") return "📝";
    if (type === "data" || ext === "csv" || ext === "tsv" || ext === "xlsx" || ext === "xls") return "📊";
    if (type === "image" || ["png", "jpg", "jpeg", "webp", "gif"].includes(ext)) return "🖼️";
    if (type === "code" || ["py", "js", "jsx", "ts", "tsx", "html", "css", "json", "sql"].includes(ext)) return "💻";
    return "📎";
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return "";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const readFileAsText = (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result || "");
      reader.onerror = () => resolve("");
      reader.readAsText(file);
    });
  };

  const handleUploadFiles = async (fileList) => {
    if (!fileList || fileList.length === 0) return;
    setUploadingFile(true);
    const newAttachments = [];

    for (const file of Array.from(fileList)) {
      let uploaded = false;

      // 1. Try backend /upload endpoint
      try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API}/upload`, {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          if (data.status === "success") {
            newAttachments.push({
              filename: data.filename || file.name,
              file_path: data.file_path || file.name,
              extracted_text: data.extracted_text || "",
              file_type: data.file_type || "document",
              file_size: data.file_size || file.size,
            });
            uploaded = true;
          }
        }
      } catch (err) {
        console.warn("Backend upload failed, attempting browser fallback:", err);
      }

      // 2. Client-side fallback if backend was unreachable
      if (!uploaded) {
        const ext = (file.name.split(".").pop() || "").toLowerCase();
        let extracted = "";
        if (["csv", "tsv", "txt", "md", "json", "py", "js", "html", "css", "sql"].includes(ext)) {
          extracted = await readFileAsText(file);
        }
        newAttachments.push({
          filename: file.name,
          file_path: file.name,
          extracted_text: extracted ? extracted.slice(0, 8000) : `[Attached local file: ${file.name}]`,
          file_type: ext === "csv" || ext === "tsv" ? "data" : "document",
          file_size: file.size,
        });
      }
    }

    if (newAttachments.length > 0) {
      setAttachedFiles((prev) => [...prev, ...newAttachments]);
    }
    setUploadingFile(false);
  };

  async function sendMessage(text) {
    const trimmed = text ? text.trim() : "";
    if ((!trimmed && attachedFiles.length === 0) || loading) return;

    const filesToSend = [...attachedFiles];
    const displayMessage = trimmed || (filesToSend.length > 0 ? `Please analyze: ${filesToSend.map((f) => f.filename).join(", ")}` : "");

    setMessages((m) => [
      ...m,
      { role: "user", content: displayMessage, files: filesToSend },
      { role: "assistant", content: "" },
    ]);
    setInput("");
    setAttachedFiles([]);
    setLoading(true);

    let accumulatedReply = "";

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, files: filesToSend }),
      });

      if (!res.ok || !res.body) {
        throw new Error("Stream connection failed");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunkStr = decoder.decode(value, { stream: true });
          const lines = chunkStr.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const dataStr = line.slice(6).trim();
              if (dataStr === "[DONE]") break;
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.chunk) {
                  accumulatedReply += parsed.chunk;
                  setMessages((prev) => {
                    const next = [...prev];
                    next[next.length - 1] = {
                      role: "assistant",
                      content: accumulatedReply,
                    };
                    return next;
                  });
                }
              } catch {
                // ignore
              }
            }
          }
        }
      }
      setLastSpeech(accumulatedReply || "Done.");
      fetchHistory();
      fetchTodos();
      fetchEvents();
      fetchSystem();
    } catch {
      // Fallback
      try {
        const fallbackRes = await fetch(`${API}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: trimmed, files: filesToSend }),
        });
        if (!fallbackRes.ok) {
          const errData = await fallbackRes.json().catch(() => ({}));
          throw new Error(errData.detail || `Server returned status ${fallbackRes.status}`);
        }
        const fallbackData = await fallbackRes.json();
        const fallbackReply = fallbackData.reply || "Done.";
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: "assistant", content: fallbackReply };
          return next;
        });
        setLastSpeech(fallbackReply);
        fetchHistory();
        fetchTodos();
        fetchEvents();
        fetchSystem();
      } catch (err) {
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            role: "assistant",
            content: `Backend error: ${err.message || "Could not reach backend. Run: python api/server.py"}`,
          };
          return next;
        });
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleVoice() {
    if (loading) return;
    setLoading(true);
    setVoiceStatus("Listening with Whisper Turbo (~150ms)...");

    try {
      const res = await fetch(`${API}/voice`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Voice recognition failed.");

      setLastSpeech(data.reply);
      setMessages((m) => [
        ...m,
        { role: "user", content: data.text },
        { role: "assistant", content: data.reply },
      ]);
      setVoiceStatus(`Transcribed: "${data.text}"`);
      fetchHistory();
      fetchTodos();
      fetchEvents();
    } catch (err) {
      setVoiceStatus(err.message || "Microphone timeout or recognition error.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    try {
      await fetch(`${API}/reset`, { method: "POST" });
      setMessages([]);
      setLastSpeech(`Session reset. How can I assist you, ${userName}?`);
    } catch {}
  }

  function handleQuickPrompt(prompt) {
    sendMessage(prompt);
    setActiveTab("chat");
  }

  return (
    <div className="desktop-app-layout">
      {/* =========================================
          LEFT DESKTOP SIDEBAR
         ========================================= */}
      <aside className="desktop-sidebar">
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-logo-glow">
            <svg viewBox="0 0 100 100" width="38" height="38" className="brand-robot-svg">
              <rect x="20" y="24" width="60" height="46" rx="16" fill="#f1f3fd" />
              <rect x="28" y="32" width="44" height="30" rx="10" fill="#120826" />
              <circle cx="40" cy="46" r="5.5" fill="#00f2fe" />
              <circle cx="60" cy="46" r="5.5" fill="#ec4899" />
              <path d="M 44 54 Q 50 57 56 54" fill="none" stroke="#00f2fe" strokeWidth="2" strokeLinecap="round" />
              <circle cx="36" cy="14" r="3.5" fill="#00f2fe" />
              <line x1="36" y1="14" x2="36" y2="24" stroke="#c2c7e6" strokeWidth="2.5" />
              <circle cx="64" cy="14" r="3.5" fill="#00f2fe" />
              <line x1="64" y1="14" x2="64" y2="24" stroke="#c2c7e6" strokeWidth="2.5" />
            </svg>
          </div>
          <div className="brand-text-col">
            <h2 className="brand-title">Echo Mind</h2>
            <span className="brand-badge">Daily Copilot Pro</span>
          </div>
        </div>

        {/* User Profile Card */}
        <div className="user-profile-badge">
          <div className="avatar-ring">
            <div className="user-avatar-initial">{userName ? userName.charAt(0).toUpperCase() : "U"}</div>
          </div>
          <div className="profile-info">
            {editingName ? (
              <input
                type="text"
                value={tempName}
                autoFocus
                onChange={(e) => setTempName(e.target.value)}
                onBlur={() => saveUserName(tempName)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") saveUserName(tempName);
                  if (e.key === "Escape") setEditingName(false);
                }}
                className="profile-name-input"
                style={{
                  background: "#1e1e38",
                  color: "#fff",
                  border: "1px solid #00f2fe",
                  borderRadius: "4px",
                  padding: "2px 6px",
                  fontSize: "0.85rem",
                  width: "110px",
                }}
              />
            ) : (
              <h4
                className="profile-name"
                title="Click to change your name"
                style={{ cursor: "pointer" }}
                onClick={() => {
                  setTempName(userName);
                  setEditingName(true);
                }}
              >
                {userName} <span style={{ fontSize: "0.7rem", opacity: 0.6 }}>✏️</span>
              </h4>
            )}
          
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <HomeIcon />
            <span>Dashboard</span>
          </button>

          <button
            className={`nav-item ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            <ChatIcon />
            <span>Chat Studio</span>
            {messages.length > 0 && <span className="nav-counter">{messages.length}</span>}
          </button>

          <button
            className={`nav-item ${activeTab === "voice" ? "active" : ""}`}
            onClick={() => setActiveTab("voice")}
          >
            <MicIcon />
            <span>Voice Assessment</span>
          </button>

          <button
            className={`nav-item ${activeTab === "agenda" ? "active" : ""}`}
            onClick={() => setActiveTab("agenda")}
          >
            <CalendarIcon />
            <span>Tasks & Agenda</span>
            {todos.filter((t) => t.status === "pending").length > 0 && (
              <span className="nav-counter task-counter">
                {todos.filter((t) => t.status === "pending").length}
              </span>
            )}
          </button>

          <button
            className={`nav-item ${activeTab === "workflows" ? "active" : ""}`}
            onClick={() => setActiveTab("workflows")}
          >
            <WorkflowIcon />
            <span>Workflows & Tools</span>
          </button>

          <button
            className={`nav-item ${activeTab === "email" ? "active" : ""}`}
            onClick={() => {
              setActiveTab("email");
              fetchGmailStatus();
              fetchGmailMessages();
            }}
          >
            <MailIcon />
            <span>Gmail Copilot</span>
          
          </button>
        </nav>

        {/* Sidebar Footer with Reset & Info */}
        <div className="sidebar-footer">
          <button className="reset-session-btn" onClick={handleReset} title="Clear conversation history">
            <TrashIcon />
            <span>Clear Session</span>
          </button>
          <div className="provider-tag-pill" title={provider}>
            <span className="provider-dot"></span>
            <span className="provider-text">{provider}</span>
          </div>
        </div>
      </aside>

      {/* =========================================
          MAIN DESKTOP WORKSPACE
         ========================================= */}
      <main className="desktop-workspace">
        {/* Top Header Bar */}
        <header className="desktop-top-header">
          <div className="header-greeting">
            <h1>
              Welcome back, <span className="name-highlight">{userName}</span>!
            </h1>
            <p>Your AI copilot is equipped with document, data, research, and system automation tools.</p>
          </div>

          <div className="header-actions">
            {/* Live Hardware Gauges */}
            <div className="system-gauge-pill" title="Live PC Hardware Diagnostics">
              <CpuIcon />
              <span>CPU: {systemStats.cpu_percent}%</span>
              <span className="gauge-divider">|</span>
              <span>RAM: {systemStats.ram_percent}% ({systemStats.ram_used_gb} GB)</span>
            </div>

            <div className="header-notifications-wrapper" ref={notifDropdownRef}>
              <button
                className={`header-icon-btn ${showNotificationsDropdown ? "active" : ""}`}
                onClick={() => {
                  fetchTodos();
                  fetchEvents();
                  setShowNotificationsDropdown((prev) => !prev);
                }}
                title="Notifications & Upcoming Tasks"
              >
                <BellIcon />
                {(notifications.length > 0 || todos.filter((t) => t.status === "pending" && t.due_date).length > 0) && (
                  <span className="badge-ping"></span>
                )}
                {notifications.length > 0 && (
                  <span className="notif-badge-pill">{notifications.length}</span>
                )}
              </button>

              {/* Notifications Popover Dropdown */}
              {showNotificationsDropdown && (
                <div className="notifications-dropdown-menu">
                  <div className="dropdown-header">
                    <div className="dropdown-title">
                      <span className="title-icon">🔔</span>
                      <h4>Notifications & Deadlines</h4>
                    </div>
                    {notifications.length > 0 && (
                      <button
                        className="clear-all-notifs-btn"
                        onClick={() => setNotifications([])}
                      >
                        Dismiss All
                      </button>
                    )}
                  </div>

                  <div className="dropdown-body-scroll">
                    {/* 1. Approaching Alerts (High Priority) */}
                    {notifications.length > 0 && (
                      <div className="dropdown-section">
                        <div className="section-label-alert">
                          <span>⏰ Approaching Deadlines</span>
                        </div>
                        {notifications.map((notif) => (
                          <div key={notif.id} className="dropdown-alert-card">
                            <div className="alert-card-info">
                              <span className="alert-card-title">{notif.title}</span>
                              <p className="alert-card-sub">{notif.text}</p>
                            </div>
                            <div className="alert-card-actions">
                              <button
                                className="alert-btn-complete"
                                onClick={() => {
                                  toggleTodo(notif.taskId);
                                  setNotifications((prev) => prev.filter((n) => n.id !== notif.id));
                                }}
                                title="Mark as completed"
                              >
                                ✓
                              </button>
                              <button
                                className="alert-btn-dismiss"
                                onClick={() => setNotifications((prev) => prev.filter((n) => n.id !== notif.id))}
                                title="Dismiss"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* 2. Tasks Due Soon */}
                    {todos.filter((t) => t.status === "pending" && t.due_date).length > 0 && (
                      <div className="dropdown-section">
                        <div className="section-label">
                          <span>Upcoming Tasks With Due Dates</span>
                        </div>
                        {todos
                          .filter((t) => t.status === "pending" && t.due_date)
                          .slice(0, 5)
                          .map((task) => (
                            <div key={task.id} className="dropdown-task-row">
                              <input
                                type="checkbox"
                                checked={task.status === "completed"}
                                onChange={() => toggleTodo(task.id)}
                              />
                              <div className="dropdown-task-text">
                                <span className="dropdown-task-title">{task.title}</span>
                                <span className="dropdown-task-due">Due: {task.due_date}</span>
                              </div>
                            </div>
                          ))}
                      </div>
                    )}

                    {/* Empty State */}
                    {notifications.length === 0 &&
                      todos.filter((t) => t.status === "pending" && t.due_date).length === 0 && (
                        <div className="dropdown-empty-state">
                          <p className="empty-title">You're all caught up!</p>
                          <span className="empty-subtitle">No approaching deadlines or urgent alerts right now.</span>
                        </div>
                      )}
                  </div>

                  <div className="dropdown-footer">
                    <button
                      className="dropdown-footer-link"
                      onClick={() => {
                        setActiveTab("agenda");
                        setShowNotificationsDropdown(false);
                      }}
                    >
                      Open Tasks & Agenda Studio ›
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Floating Approaching Task Notifications */}
        {notifications.length > 0 && (
          <div className="floating-notifications-container">
            {notifications.map((notif) => (
              <div key={notif.id} className="task-notification-toast">
                <div className="notif-header">
                  <strong>
                    <span className="notif-icon">⏰</span> Task Approaching!
                  </strong>
                  <button
                    className="notif-close-btn"
                    onClick={() => setNotifications((prev) => prev.filter((n) => n.id !== notif.id))}
                    title="Dismiss notification"
                  >
                    ✕
                  </button>
                </div>
                <p className="notif-body">{notif.text}</p>
                <div className="notif-actions">
                  <button
                    className="notif-btn-complete"
                    onClick={() => {
                      toggleTodo(notif.taskId);
                      setNotifications((prev) => prev.filter((n) => n.id !== notif.id));
                    }}
                  >
                    ✓ Complete Task
                  </button>
                  <button
                    className="notif-btn-dismiss"
                    onClick={() => setNotifications((prev) => prev.filter((n) => n.id !== notif.id))}
                  >
                    Snooze
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Content Views */}
        <div className="workspace-scroll-area">
          {/* 1. DASHBOARD VIEW */}
          {activeTab === "dashboard" && (
            <div className="dashboard-view-container">
              {/* Quick Action Large Cards */}
              <div className="action-cards-deck">
                <div className="desktop-action-card card-chat" onClick={() => setActiveTab("chat")}>
                  <div className="card-top-icon">
                    <ChatIcon />
                  </div>
                  <div className="card-content-block">
                    <span className="card-subtitle">Chat with</span>
                    <h3 className="card-main-title">Echo Mind</h3>
                    <p className="card-desc">Execute real-time streaming queries, analyze local documents, extract data, and draft communications.</p>
                  </div>
                  <div className="card-arrow-pill">Open Studio ›</div>
                </div>

                <div className="desktop-action-card card-voice" onClick={() => setActiveTab("voice")}>
                  <div className="card-top-icon voice-icon-bg">
                    <MicIcon />
                  </div>
                  <div className="card-content-block">
                    <span className="card-subtitle">Talk with</span>
                    <h3 className="card-main-title">Echo Mind</h3>
                    <p className="card-desc">Sub-second Whisper Turbo voice recognition .</p>
                  </div>
                  <div className="card-arrow-pill voice-pill">Voice Mode ›</div>
                </div>
              </div>

              {/* 5 Productivity Super-Pillars Grid */}
              <div className="desktop-section-panel">
                <div className="section-title-row">
                  <h3>Daily Productivity Copilot Hub</h3>
                  <span className="section-sublink" onClick={() => handleQuickPrompt("Give me my daily briefing with pending tasks, calendar events, and PC status")}>
                    ☀️ Daily Briefing ›
                  </span>
                </div>
                <div className="super-pillars-grid">
                  <div className="pillar-tile" onClick={() => handleQuickPrompt("Search documents in my documents folder for project notes")}>
                    <div className="pillar-icon doc-color"><DocIcon /></div>
                    <h4>Document Brain</h4>
                    <p>Read & summarize PDFs, DOCX, text</p>
                  </div>

                  <div className="pillar-tile" onClick={() => handleQuickPrompt("Perform deep web research comparing top AI coding assistants in 2026")}>
                    <div className="pillar-icon research-color"><GlobeIcon /></div>
                    <h4>Deep Research</h4>
                    <p>Headless multi-source web synthesis</p>
                  </div>

                  <div className="pillar-tile" onClick={() => handleQuickPrompt("Inspect my CSV dataset at data/test_sample.csv and generate a chart")}>
                    <div className="pillar-icon chart-color"><ChartIcon /></div>
                    <h4>Data & Charts</h4>
                    <p>CSV / Excel stats & auto-plots</p>
                  </div>

                  <div className="pillar-tile" onClick={() => handleQuickPrompt("Inspect system resources and list top memory-heavy processes")}>
                    <div className="pillar-icon sys-color"><CpuIcon /></div>
                    <h4>System Diagnostics</h4>
                    <p>Live RAM, CPU, disk & temp cleanup</p>
                  </div>

                  <div className="pillar-tile" onClick={() => { setActiveTab("email"); fetchGmailStatus(); fetchGmailMessages(); }}>
                    <div className="pillar-icon email-color"><MailIcon /></div>
                    <h4>Gmail & Drafts</h4>
                    <p>Read inbox & auto-draft replies</p>
                  </div>

                  <div className="pillar-tile" onClick={() => setActiveTab("agenda")}>
                    <div className="pillar-icon cal-color"><CalendarIcon /></div>
                    <h4>Agenda & Tasks</h4>
                    <p>Manage to-dos & upcoming events</p>
                  </div>
                </div>
              </div>

              {/* Two Column Grid: Tasks/History + Live Voice Widget */}
              <div className="dashboard-split-grid">
                {/* Left: Tasks & Agenda Preview */}
                <div className="desktop-card-panel history-panel">
                  <div className="panel-header-line">
                    <h3>Pending Tasks & Agenda</h3>
                    <span className="refresh-link" onClick={() => setActiveTab("agenda")}>Manage All ›</span>
                  </div>
                  <div className="tasks-preview-list">
                    {todos.filter((t) => t.status === "pending").length === 0 ? (
                      <div className="empty-tasks-box">
                        <p>No pending tasks! All caught up.</p>
                        <button className="add-task-shortcut" onClick={() => handleQuickPrompt("Add a task to review quarterly report tomorrow")}>
                          + Add a Task
                        </button>
                      </div>
                    ) : (
                      todos
                        .filter((t) => t.status === "pending")
                        .slice(0, 5)
                        .map((task) => (
                          <div key={task.id} className="task-preview-row">
                            <input
                              type="checkbox"
                              className="task-check"
                              onChange={() => toggleTodo(task.id)}
                            />
                            <div className="task-text-col">
                              <span className="task-title-text">{task.title}</span>
                              {task.due_date && <span className="task-due-tag">Due: {task.due_date}</span>}
                            </div>
                            <button
                              className="task-delete-btn"
                              onClick={(e) => deleteTodo(task.id, e)}
                              title="Delete task"
                            >
                              <TrashIcon />
                            </button>
                          </div>
                        ))
                    )}
                  </div>
                </div>

                {/* Right: Interactive Voice Orb Widget */}
                <div className="desktop-card-panel voice-widget-panel">
                  <div className="panel-header-line">
                    <h3>Voice Assessment</h3>
                    <span className="voice-live-badge">{loading ? "Listening..." : "Whisper Turbo"}</span>
                  </div>
                  <div className="vortex-desktop-wrapper">
                    <FluidVortex isActive={loading} size={230} />
                  </div>
                  <p className="voice-preview-caption">{lastSpeech}</p>
                  <div className="widget-mic-controls">
                    <button
                      className={`desktop-giant-mic ${loading ? "recording-pulse" : ""}`}
                      onClick={handleVoice}
                      disabled={loading}
                      title="Click to speak"
                    >
                      <MicIcon />
                    </button>
                    <span className="mic-hint-text">{voiceStatus}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. CHAT STUDIO VIEW */}
          {activeTab === "chat" && (
            <div className="chat-studio-container">
              <div className="chat-messages-scroll">
                {messages.length === 0 ? (
                  <div className="desktop-empty-chat">
                    <div className="empty-robot-illustration">
                      <svg viewBox="0 0 100 100" width="60" height="60">
                        <rect x="20" y="24" width="60" height="46" rx="16" fill="#f1f3fd" />
                        <rect x="28" y="32" width="44" height="30" rx="10" fill="#120826" />
                        <circle cx="40" cy="46" r="5.5" fill="#00f2fe" />
                        <circle cx="60" cy="46" r="5.5" fill="#ec4899" />
                        <path d="M 44 54 Q 50 57 56 54" fill="none" stroke="#00f2fe" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                    </div>
                    <h2>How can Echo Mind empower your day, {userName}?</h2>
                    <p>I can read your documents, analyze spreadsheets, research topics online, check PC health, or manage your schedule.</p>
                    <div className="suggestion-chips-grid">
                      <button onClick={() => sendMessage("Give me my daily briefing with pending tasks, agenda, and PC health")}>
                        ☀️ "Give me my daily briefing"
                      </button>
                      <button onClick={() => sendMessage("Perform deep web research comparing PostgreSQL vs SQLite for local apps")}>
                        🌐 "Deep research PostgreSQL vs SQLite"
                      </button>
                      <button onClick={() => sendMessage("Inspect my system resources and tell me what is using RAM")}>
                        💻 "Check PC RAM & CPU usage"
                      </button>
                      <button onClick={() => sendMessage("Draft a professional email proposing a project kickoff next Monday")}>
                        ✉️ "Draft project kickoff email"
                      </button>
                    </div>
                  </div>
                ) : (
                  messages.map((msg, i) => (
                    <div key={i} className={`desktop-chat-bubble ${msg.role}`}>
                      <div className="bubble-header-tag">
                        <span className="author-tag">{msg.role === "user" ? userName : "Echo Mind"}</span>
                      </div>
                      {/* Attached files badge inside message bubble */}
                      {msg.files && msg.files.length > 0 && (
                        <div className="message-files-container">
                          {msg.files.map((f, fIdx) => (
                            <div key={fIdx} className="message-file-badge">
                              <span className="file-badge-icon">{getFileIcon(f.file_type, f.filename)}</span>
                              <div className="file-badge-details">
                                <span className="file-badge-name" title={f.filename}>{f.filename}</span>
                                <span className="file-badge-size">{formatFileSize(f.file_size)} • {f.file_type || "file"}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="bubble-content-text">
                        <p>{msg.content || (loading && i === messages.length - 1 ? "Thinking..." : "")}</p>
                      </div>
                    </div>
                  ))
                )}
                {loading && messages.length > 0 && messages[messages.length - 1].role === "user" && (
                  <div className="desktop-chat-bubble assistant loading-bubble">
                    <div className="bubble-header-tag">
                      <span className="author-tag">Echo Mind</span>
                    </div>
                    <div className="typing-dots-cluster">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>

              {/* Attached files preview pill bar */}
              {attachedFiles.length > 0 && (
                <div className="attached-files-bar">
                  {attachedFiles.map((f, idx) => (
                    <div key={idx} className="attached-file-pill">
                      <span className="attached-file-icon">{getFileIcon(f.file_type, f.filename)}</span>
                      <span className="attached-file-name" title={f.filename}>{f.filename}</span>
                      <span className="attached-file-size">{formatFileSize(f.file_size)}</span>
                      <button
                        type="button"
                        className="attached-file-remove"
                        onClick={() => setAttachedFiles((prev) => prev.filter((_, i) => i !== idx))}
                        title="Remove file"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                  {uploadingFile && <span className="upload-indicator">Uploading & parsing...</span>}
                </div>
              )}

              {/* Chat Input Dock with Drag & Drop */}
              <div
                className={`desktop-chat-dock ${isDraggingOver ? "dock-drag-active" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDraggingOver(true);
                }}
                onDragLeave={() => setIsDraggingOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDraggingOver(false);
                  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    handleUploadFiles(e.dataTransfer.files);
                  }
                }}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: "none" }}
                  accept=".csv,.xlsx,.xls,.tsv,.pdf,.docx,.doc,.txt,.md,.json,.py,.js,.html,.css,.png,.jpg,.jpeg,.webp"
                  multiple
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      handleUploadFiles(e.target.files);
                    }
                    e.target.value = "";
                  }}
                />
                <button
                  type="button"
                  className="dock-action-btn attach-btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading || uploadingFile}
                  title="Attach files (PDF, Word, CSV, Excel, Code, Images)"
                >
                  <PaperclipIcon />
                </button>
                <input
                  type="text"
                  placeholder={
                    uploadingFile
                      ? "Uploading & extracting document..."
                      : attachedFiles.length > 0
                      ? `Ask Echo Mind about ${attachedFiles.length} attached file(s)...`
                      : "Ask Echo Mind to analyze files, research online, create charts, or manage tasks..."
                  }
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
                  disabled={loading || uploadingFile}
                />
                <button
                  className="dock-action-btn mic-btn"
                  onClick={handleVoice}
                  disabled={loading}
                  title="Speak command"
                >
                  <MicIcon />
                </button>
                <button
                  className="dock-send-button"
                  onClick={() => sendMessage(input)}
                  disabled={loading || uploadingFile || (!input.trim() && attachedFiles.length === 0)}
                >
                  Send
                </button>
              </div>
            </div>
          )}

          {/* 3. VOICE ASSESSMENT VIEW */}
          {activeTab === "voice" && (
            <div className="voice-studio-container">
              <div className="voice-studio-header">
                <h2>Voice Assessment Studio</h2>
                <p className="voice-studio-sub">{voiceStatus}</p>
              </div>

              <div className="voice-canvas-centerpiece">
                <FluidVortex isActive={loading} size={360} />
              </div>

              <div className="voice-transcript-card">
                <span className="transcript-label">Transcript & Output</span>
                <p className="transcript-body">{lastSpeech}</p>
              </div>

              <div className="voice-studio-dock">
                <button
                  className={`voice-huge-mic ${loading ? "recording-pulse" : ""}`}
                  onClick={handleVoice}
                  disabled={loading}
                >
                  <MicIcon />
                </button>
                <p className="mic-dock-instruction">Click the microphone to speak with Whisper Turbo (~150ms)</p>
              </div>
            </div>
          )}

          {/* 4. AGENDA & TASKS VIEW */}
          {activeTab === "agenda" && (
            <div className="agenda-studio-container">
              <div className="section-title-row">
                <div>
                  <h2>Tasks & Agenda Manager</h2>
                  <p className="section-subtitle">Keep track of your deadlines, appointments, and daily to-do items.</p>
                </div>
                <button
                  className="quick-action-pill-btn"
                  onClick={() => handleQuickPrompt("Give me my daily briefing with pending tasks, agenda, and PC health")}
                >
                  ☀️ Morning Briefing
                </button>
              </div>

              <div className="agenda-two-col-grid">
                {/* To-Do Column */}
                <div className="agenda-card-panel">
                  <div className="panel-header-line">
                    <h3>To-Do Tasks ({todos.length})</h3>
                    <button
                      className="small-action-btn"
                      onClick={() => setShowNewTodoForm((prev) => !prev)}
                    >
                      {showNewTodoForm ? "✕ Cancel" : "+ New Task"}
                    </button>
                  </div>

                  {showNewTodoForm && (
                    <form className="inline-add-task-form" onSubmit={handleCreateNewTodo}>
                      <input
                        type="text"
                        className="new-task-input"
                        placeholder="What do you need to get done?"
                        value={newTodoTitle}
                        onChange={(e) => setNewTodoTitle(e.target.value)}
                        autoFocus
                      />
                      <div className="inline-add-task-row">
                        <input
                          type="text"
                          className="new-task-date-input"
                          placeholder="Due (e.g. 15:30, 2026-10-15 17:00)"
                          value={newTodoDueDate}
                          onChange={(e) => setNewTodoDueDate(e.target.value)}
                        />
                        <button type="submit" className="new-task-submit-btn">
                          Add Task
                        </button>
                        <button
                          type="button"
                          className="new-task-cancel-btn"
                          onClick={() => {
                            setShowNewTodoForm(false);
                            setNewTodoTitle("");
                            setNewTodoDueDate("");
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}
                  <div className="agenda-items-scroll">
                    {todos.length === 0 ? (
                      <p className="agenda-empty-text">No tasks recorded. Add one using voice or chat!</p>
                    ) : (
                      todos.map((t) => (
                        <div key={t.id} className={`agenda-item-card ${t.status === "completed" ? "completed" : ""}`}>
                          <input
                            type="checkbox"
                            checked={t.status === "completed"}
                            onChange={() => toggleTodo(t.id)}
                          />
                          <div className="agenda-item-info">
                            <h4 className="agenda-item-title">{t.title}</h4>
                            <span className="agenda-item-meta">{t.due_date ? `Due: ${t.due_date} • ` : ""}Created: {t.created_at.slice(0, 10)}</span>
                          </div>
                          <button
                            className="task-delete-btn"
                            onClick={(e) => deleteTodo(t.id, e)}
                            title="Delete task"
                          >
                            <TrashIcon />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Calendar Events Column */}
                <div className="agenda-card-panel">
                  <div className="panel-header-line">
                    <h3>Upcoming Events & Meetings ({events.length})</h3>
                    <button
                      className="small-action-btn"
                      onClick={() => setShowNewEventForm((prev) => !prev)}
                    >
                      {showNewEventForm ? "✕ Cancel" : "+ New Event"}
                    </button>
                  </div>

                  {showNewEventForm && (
                    <form className="inline-add-task-form" onSubmit={handleCreateNewEvent}>
                      <input
                        type="text"
                        className="new-task-input"
                        placeholder="Meeting or event title..."
                        value={newEventTitle}
                        onChange={(e) => setNewEventTitle(e.target.value)}
                        autoFocus
                      />
                      <div className="inline-add-task-row">
                        <input
                          type="text"
                          className="new-task-date-input"
                          placeholder="Date (e.g. 2026-10-16, Today)"
                          value={newEventDate}
                          onChange={(e) => setNewEventDate(e.target.value)}
                        />
                        <input
                          type="text"
                          className="new-task-date-input"
                          placeholder="Time (e.g. 14:00, 2:30 PM)"
                          style={{ maxWidth: "130px" }}
                          value={newEventTime}
                          onChange={(e) => setNewEventTime(e.target.value)}
                        />
                        <button type="submit" className="new-task-submit-btn">
                          Schedule
                        </button>
                        <button
                          type="button"
                          className="new-task-cancel-btn"
                          onClick={() => {
                            setShowNewEventForm(false);
                            setNewEventTitle("");
                            setNewEventDate("");
                            setNewEventTime("");
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}

                  <div className="agenda-items-scroll">
                    {events.length === 0 ? (
                      <p className="agenda-empty-text">No calendar events scheduled.</p>
                    ) : (
                      events.map((evt) => (
                        <div key={evt.id} className="agenda-item-card event-card">
                          <div className="event-date-badge">
                            <span>{evt.date}</span>
                            {evt.time && <small>{evt.time}</small>}
                          </div>
                          <div className="agenda-item-info">
                            <h4 className="agenda-item-title">{evt.title}</h4>
                            {evt.notes && <p className="agenda-item-notes">{evt.notes}</p>}
                          </div>
                          <button
                            className="task-delete-btn"
                            onClick={(clickEvt) => deleteEvent(evt.id, clickEvt)}
                            title="Delete event"
                          >
                            <TrashIcon />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5. WORKFLOWS & TOOLS VIEW */}
          {activeTab === "workflows" && (
            <div className="workflows-studio-container">
              <div className="section-title-row">
                <h2>Automated Workflows</h2>
                <span className="section-subtitle">Multi-step sequences ready to run</span>
              </div>

              <div className="workflows-cards-grid">
                {workflows.map((wf) => (
                  <div key={wf.id} className="workflow-card">
                    <div className="wf-icon-box">
                      <WorkflowIcon />
                    </div>
                    <div className="wf-info">
                      <h3>{wf.name}</h3>
                      <p>{wf.description}</p>
                    </div>
                    <button className="run-wf-btn" onClick={() => handleQuickPrompt(`Run the ${wf.id} workflow`)}>
                      Run Workflow
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 6. GMAIL INBOX & COPILOT VIEW */}
          {activeTab === "email" && (
            <div className="gmail-studio-container">
              {/* Connection Status Banner */}
              <div className="gmail-status-card">
                <div className="gmail-status-info">
                  <div className="section-title-row" style={{ marginBottom: 0 }}>
                    <h2>Gmail Inbox & AI Draft Copilot</h2>
                  </div>
                  <div className="gmail-status-hint">
                    {gmailStatus.configured && gmailStatus.connected ? (
                      <span className="gmail-status-badge gmail-badge-connected">
                        ● Connected: {gmailStatus.email}
                      </span>
                    ) : (
                      <span className="gmail-status-badge gmail-badge-offline">
                        ● Not Connected
                      </span>
                    )}
                    <span style={{ marginLeft: "8px" }}>
                      {gmailStatus.configured && gmailStatus.connected
                        ? "AI email reading, smart drafting, and inbox automation ready."
                        : "Connect any standard Gmail account in 60 seconds (100% free)."}
                    </span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap" }}>
                  {gmailStatus.configured && gmailStatus.connected ? (
                    <>
                      <button
                        className="gmail-btn-secondary"
                        onClick={() => {
                          setShowConnectCard((prev) => !prev);
                          setHideConnectedCard(false);
                        }}
                        title={showConnectCard ? "Hide Settings" : "Account Settings"}
                      >
                        ⚙️ {showConnectCard ? "Hide Settings" : "Account Settings"}
                      </button>
                      <button
                        className="gmail-btn-secondary gmail-btn-danger-outline"
                        onClick={handleDisconnectGmail}
                        title="Disconnect email"
                      >
                        Unlink
                      </button>
                    </>
                  ) : (
                    <button
                      className="gmail-btn-secondary"
                      onClick={() => {
                        setShowConnectCard(true);
                        setConnectCardDismissed(false);
                      }}
                      title="Connect Gmail account"
                    >
                      ➕ Connect Account
                    </button>
                  )}
                  <button
                    className="gmail-btn-secondary"
                    onClick={() => {
                      fetchGmailStatus();
                      fetchGmailMessages();
                    }}
                    title="Refresh Gmail connection and messages"
                  >
                    🔄 Sync Gmail
                  </button>
                </div>
              </div>

              {/* Main Two-Column Layout */}
              <div className="gmail-grid-layout">
                {/* Column 1: Inbox Reader */}
                <div className="gmail-card-panel">
                  <div className="gmail-panel-header">
                    <div>
                      <h3>Recent Inbox Emails</h3>
                      <p className="section-subtitle">Read messages, summarize content, or generate AI replies</p>
                    </div>
                    <button
                      className="gmail-btn-secondary"
                      onClick={fetchGmailMessages}
                      disabled={gmailLoading}
                    >
                      {gmailLoading ? "Loading..." : "Refresh Inbox"}
                    </button>
                  </div>

                  <div className="gmail-messages-list">
                    {!Array.isArray(gmailMessages) || gmailMessages.length === 0 ? (
                      <div className="agenda-empty-text">
                        {gmailLoading
                          ? "Fetching emails from Gmail..."
                          : gmailStatus?.configured
                          ? "No recent emails found in inbox. Click 'Refresh Inbox' to sync."
                          : "Configure your Gmail credentials below to view your inbox."}
                      </div>
                    ) : (
                      gmailMessages.map((msg, idx) => (
                        <div key={msg.id || idx} className="gmail-message-item">
                          <div className="gmail-msg-top">
                            <span className="gmail-msg-from">{msg.from || "Unknown Sender"}</span>
                            <span>
                              {msg.date
                                ? (() => {
                                    try {
                                      const d = new Date(msg.date);
                                      return isNaN(d.getTime()) ? String(msg.date).slice(0, 16) : d.toLocaleDateString();
                                    } catch {
                                      return "";
                                    }
                                  })()
                                : ""}
                            </span>
                          </div>
                          <div className="gmail-msg-subject">{msg.subject || "(No Subject)"}</div>
                          <div className="gmail-msg-actions">
                            <button
                              className="gmail-ai-chip"
                              onClick={() => {
                                setActiveTab("chat");
                                sendMessage(`Read my email from ${msg.from || "sender"} with subject "${msg.subject || ""}" (ID ${msg.id || ""}) and provide a concise summary of the action items.`);
                              }}
                            >
                              ✨ Summarize with AI
                            </button>
                            <button
                              className="gmail-ai-chip"
                              onClick={() => {
                                setActiveTab("chat");
                                sendMessage(`Read email ID ${msg.id || ""} from ${msg.from || "sender"} with subject "${msg.subject || ""}" and draft a polite, professional reply to them.`);
                              }}
                            >
                              ✍️ AI Draft Reply
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Column 2: Account Setup & Quick Compose */}
                <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
                  {/* Connected Account Summary (Compact & Removable with ✕) */}
                  {gmailStatus?.configured && gmailStatus?.connected && !showConnectCard && !hideConnectedCard && (
                    <div className="gmail-connected-card">
                      <div className="gmail-connected-info">
                        <div className="gmail-connected-avatar">
                          {typeof gmailStatus?.email === "string" && gmailStatus.email.length > 0
                            ? gmailStatus.email[0].toUpperCase()
                            : "G"}
                        </div>
                        <div className="gmail-connected-details">
                          <div className="gmail-connected-header-line">
                            <span className="gmail-connected-badge-dot"></span>
                            <span className="gmail-connected-status-text">Connected Gmail</span>
                          </div>
                          <span className="gmail-connected-email" title={gmailStatus?.email || ""}>
                            {gmailStatus?.email || ""}
                          </span>
                        </div>
                      </div>
                      <div className="gmail-connected-btn-group">
                        <button
                          className="gmail-btn-mini"
                          onClick={() => setShowConnectCard(true)}
                          title="Change credentials or reconnect"
                        >
                          ⚙️ Change
                        </button>
                        <button
                          className="gmail-btn-mini gmail-btn-danger"
                          onClick={handleDisconnectGmail}
                          title="Remove account credentials"
                        >
                          Disconnect
                        </button>
                        <button
                          className="gmail-card-close-btn"
                          onClick={() => setHideConnectedCard(true)}
                          title="Remove from screen (close)"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Account Setup Card (Removable with ✕ and Close button) */}
                  {(showConnectCard || (!gmailStatus.connected && !connectCardDismissed)) && (
                    <div className="gmail-card-panel gmail-connect-panel">
                      <div className="gmail-panel-header">
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <MailIcon />
                          <h3>{gmailStatus.connected ? "Update Gmail Connection" : "Connect Your Gmail Account"}</h3>
                        </div>
                        <button
                          className="gmail-card-close-btn"
                          onClick={() => {
                            setShowConnectCard(false);
                            setConnectCardDismissed(true);
                          }}
                          title="Close / Remove this panel"
                          aria-label="Close"
                        >
                          ✕
                        </button>
                      </div>
                      <p style={{ fontSize: "0.8rem", color: "#a78bfa", lineHeight: 1.45 }}>
                        Use a free 16-character Google App Password. Create one for free at{" "}
                        <a
                          href="https://myaccount.google.com/apppasswords"
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: "#c084fc", textDecoration: "underline" }}
                        >
                          myaccount.google.com/apppasswords
                        </a>.
                      </p>

                      <form onSubmit={saveGmailConfig} className="gmail-form">
                        <div className="gmail-field-group">
                          <label>Gmail Address</label>
                          <input
                            type="email"
                            className="gmail-input-field"
                            placeholder="client@gmail.com"
                            value={gmailEmailInput}
                            onChange={(e) => setGmailEmailInput(e.target.value)}
                            required
                          />
                        </div>
                        <div className="gmail-field-group">
                          <label>Google App Password (16 chars)</label>
                          <input
                            type="password"
                            className="gmail-input-field"
                            placeholder="xxxx xxxx xxxx xxxx"
                            value={gmailPasswordInput}
                            onChange={(e) => setGmailPasswordInput(e.target.value)}
                            required
                          />
                        </div>
                        <div className="gmail-form-actions">
                          <button type="submit" className="gmail-btn-primary">
                            Save & Connect Account
                          </button>
                          <button
                            type="button"
                            className="gmail-btn-secondary"
                            onClick={() => {
                              setShowConnectCard(false);
                              setConnectCardDismissed(true);
                            }}
                          >
                            Close
                          </button>
                        </div>
                        {gmailConfigStatus && (
                          <div
                            className={`gmail-alert-box ${
                              String(gmailConfigStatus).includes("✅") ? "gmail-alert-success" : "gmail-alert-error"
                            }`}
                          >
                            {String(gmailConfigStatus)}
                          </div>
                        )}
                      </form>
                    </div>
                  )}


                  {/* Quick Compose / Draft Card */}
                  <div className="gmail-card-panel">
                    <div className="gmail-panel-header">
                      <h3>Draft or Send Email</h3>
                    </div>
                    <form className="gmail-form">
                      <div className="gmail-field-group">
                        <label>To (Recipient)</label>
                        <input
                          type="email"
                          className="gmail-input-field"
                          placeholder="partner@example.com"
                          value={draftRecipient}
                          onChange={(e) => setDraftRecipient(e.target.value)}
                        />
                      </div>
                      <div className="gmail-field-group">
                        <label>Subject</label>
                        <input
                          type="text"
                          className="gmail-input-field"
                          placeholder="Meeting follow-up"
                          value={draftSubject}
                          onChange={(e) => setDraftSubject(e.target.value)}
                        />
                      </div>
                      <div className="gmail-field-group">
                        <label>Message Content</label>
                        <textarea
                          className="gmail-textarea"
                          placeholder="Write your email body or draft..."
                          value={draftBody}
                          onChange={(e) => setDraftBody(e.target.value)}
                        />
                      </div>
                      <div className="gmail-form-actions">
                        <button
                          type="button"
                          className="gmail-btn-secondary"
                          style={{ flex: 1 }}
                          onClick={handleCreateDraft}
                          disabled={draftLoading}
                        >
                          Save as Draft
                        </button>
                        <button
                          type="button"
                          className="gmail-btn-primary"
                          onClick={handleSendDirect}
                          disabled={draftLoading}
                        >
                          Send Email
                        </button>
                      </div>
                      {draftResult && (
                        <div
                          className={`gmail-alert-box ${
                            String(draftResult).includes("✅") ? "gmail-alert-success" : "gmail-alert-error"
                          }`}
                        >
                          {String(draftResult)}
                        </div>
                      )}
                    </form>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
