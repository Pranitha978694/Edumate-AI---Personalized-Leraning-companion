# EduMate AI - Deep Dive Architecture & Interaction Models

This document provides a highly detailed technical breakdown of the EduMate AI platform. It covers component-level interactions, data structures, state management, and comprehensive interaction flows.

## 1. System Context & Container Diagram

The following diagram illustrates the high-level containers and their responsibilities within the EduMate AI ecosystem.

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end

    subgraph "Frontend Container (Next.js)"
        UI[React UI Components]
        State[Global Context / Hooks]
        Router[App Router]
        API_Client[Axios / Fetch Utilities]
    end

    subgraph "Backend Container (FastAPI)"
        API_Gateway[FastAPI Router]
        Service_Layer[Business Logic Services]
        Parser_Service[Document Parser Engine]
        AI_Service[Gemini Integration Service]
    end

    subgraph "Data & Auth Layer (Firebase)"
        Auth[Firebase Authentication]
        Firestore[Cloud Firestore DB]
        Storage[Firebase Storage Buckets]
    end

    Browser -->|HTTPS/User Interactions| UI
    UI -->|Updates| State
    UI -->|Navigates| Router
    State -->|Triggers| API_Client
    
    API_Client -->|JSON/Multipart| API_Gateway
    API_Client -->|SDK Calls| Auth
    API_Client -->|SDK Calls| Firestore
    
    API_Gateway -->|Routes| Service_Layer
    Service_Layer -->|Extract Text| Parser_Service
    Service_Layer -->|Analyze/Generate| AI_Service
```

---

## 2. Component Architecture (Frontend)

The frontend is structured using a component-based architecture. A central `ProjectContext` or specific hooks manage the state of the active document, quiz progress, and chat history.

### 2.1 Component Tree & Data Flow

```mermaid
graph TD
    Root[Layout.tsx] -->|Wraps| AuthProv[AuthProvider]
    AuthProv -->|Wraps| Dashboard[Dashboard Page /dashboard]
    
    Dashboard -->|Manages| UserState[User Session]
    Dashboard -->|Manages| DocState[Active Document Data]
    
    Dashboard --> Sidebar[Sidebar Nav]
    Dashboard --> MainArea[Main Content Area]
    
    MainArea --> FileUpload[File Upload Component]
    MainArea --> AnalysisView[Analysis View]
    MainArea --> QuizView[Quiz Interface]
    MainArea --> ChatView[Chat Interface]
    
    FileUpload -->|onUpload| API_Upload[POST /process]
    AnalysisView -->|Display| Summary[Summary Card]
    AnalysisView -->|Display| KeyPoints[KeyPoints List]
    AnalysisView -->|Display| Glossary[Glossary Table]
    
    QuizView -->|onStart| API_Quiz[POST /quiz]
    ChatView -->|onSubmit| API_Chat[POST /chat]
```

---

## 3. Detailed Interaction Flows

### 3.1. File Upload & Analysis Pipeline (Detailed Attributes)

This flow details the exact data attributes passed during the upload process, including error handling.

```mermaid
sequenceDiagram
    participant User
    participant UI as FileUpload.tsx
    participant State as ApplicationState
    participant API as FastAPI Backend
    participant Parser as DocParsers
    participant Gemini as Google AI
    
    User->>UI: Selects "lecture_notes.pdf"
    UI->>State: Set isUploading(true)
    UI->>API: POST /process (FormData: file=Blob)
    
    activate API
    note right of API: Validation Layer
    API->>API: Validates MimeType (application/pdf)
    
    alt Invalid File Type
        API-->>UI: 400 Bad Request ("Unsupported file")
        UI->>State: Set error("Invalid file type")
    else Valid File
        API->>Parser: extract_text(file_stream)
        Parser-->>API: returns raw_text (str)
        
        API->>Gemini: model.generate_content(Prompt + raw_text[:30k])
        Gemini-->>API: JSON String
        
        API->>API: json.loads(cleaned_response)
        
        API-->>UI: 200 OK
        note left of API: Response Body: <br/>{<br/>  "data": { "summary": "...", "keyTakeaways": [...], "glossary": [...] },<br/>  "text": "Full extracted text..."<br/>}
    end
    deactivate API
    
    UI->>State: Set activeDocument(response.data)
    UI->>State: Set isUploading(false)
    UI->>User: Shows "Analysis Complete" Toast
```

### 3.2. Quiz Session State Machine

The Quiz component operates as a finite state machine.

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Generating : User clicks "Start Quiz"
    Generating --> Ready : API returns Quiz JSON
    Generating --> Error : API Fails
    
    Ready --> QuestionActive : User starts
    
    state QuestionActive {
        [*] --> WaitingForInput
        WaitingForInput --> Selected : User clicks Option
        Selected --> Feedback : User clicks "Submit"
        Feedback --> NextQuestion : Next >
    }
    
    NextQuestion --> QuestionActive : more questions exist
    NextQuestion --> Finished : no more questions
    
    Finished --> Review : View Score
    Review --> Idle : Reset
```

### 3.3. RAG-Lite Chat Interaction (Retrieval Augmented Generation)

The chat system sends context window snippets to Gemini to simulate memory of the document.

```mermaid
sequenceDiagram
    participant User
    participant ChatUI as ChatInterface.tsx
    participant API as FastAPI /chat
    participant Gemini as AI Model
    
    User->>ChatUI: "Explain the concept of Photosynthesis"
    
    note right of ChatUI: Context Assembly
    ChatUI->>ChatUI: Retrieve 'activeDocument.text' from State
    ChatUI->>ChatUI: Slice text to 20k chars (Context Window)
    
    ChatUI->>API: POST /chat Payload
    note right of ChatUI: {<br/>  "message": "Explain...",<br/>  "context": "Photosynthesis is...",<br/>  "history": [{"role": "user", "content": "..."}]<br/>}
    
    activate API
    API->>API: Format Prompt (System + Context + UserQuery)
    API->>Gemini: chat.send_message(formatted_prompt)
    Gemini-->>API: "Photosynthesis is the process..."
    API-->>ChatUI: { "reply": "Photosynthesis is the process..." }
    deactivate API
    
    ChatUI->>ChatUI: Append to MessageList
    ChatUI->>User: Display AI Response
```

---

## 4. Backend Data Models (Pydantic)

These models define the strict contracts for API communication (FastAPI).

### 4.1. Document Analysis Response
```python
class AnalysisResult(BaseModel):
    basic: LevelInsights
    intermediate: LevelInsights
    advanced: LevelInsights
    glossary: List[GlossaryTerm]

class LevelInsights(BaseModel):
    summary: str
    keyTakeaways: List[str]

class GlossaryTerm(BaseModel):
    term: str
    definition: str
```

### 4.2. Quiz Generation
```python
class QuizRequest(BaseModel):
    text: str
    mode: str = "intermediate" # 'basic' | 'intermediate' | 'advanced'

class QuizQuestion(BaseModel):
    question: str
    options: List[str] # Array of 4 strings
    answer: str # Exact string match from options based on UI implementation
```

### 4.3. Chat Interface
```python
class ChatMessage(BaseModel):
    role: str # 'user' | 'model'
    content: str
    
class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    history: List[ChatMessage] = []
```

---

## 5. Database Schema (Firestore)

The application uses a **NoSQL** document model with a subcollection architecture to organize user data.

```mermaid
erDiagram
    USERS ||--o{ DOCUMENTS : "contains subcollection"
    
    USERS {
        string uid PK "Firebase Auth ID"
        string email
        string displayName
        timestamp createdAt
    }
    
    DOCUMENTS {
        string id PK "Auto-ID"
        string name "File Name"
        string type "MIME Type"
        number size "Bytes"
        string driveFileId "Google Drive Reference"
        string status "processed | processing | error"
        string textContent "Full extracted text"
        json parsedData "AI Analysis (Summary, KeyPoints, Glossary)"
        array chatHistory "History of Q&A with this doc"
        number readingMastery "Progress (0-100)"
        number testMastery "Quiz Score Avg (0-100)"
        timestamp createdAt
    }
```

---

## 6. Infrastructure & Deployment View

```mermaid
graph LR
    subgraph "Production Environment"
        Verifier[Vercel (Frontend)]
        Renderer[Render/Cloud Run (Backend)]
        DB[Firebase Firestore]
    end
    
    Dev[Developer Laptop] -->|git push| GitHub
    GitHub -->|Webhook| Verifier
    GitHub -->|Webhook| Renderer
    
    Verifier -->|Connects to| Renderer
    Verifier -->|Connects to| DB
```

## 7. Error Handling Strategies

| Service | Failure Mode | Fallback Strategy | User Feedback |
| :--- | :--- | :--- | :--- |
| **Gemini AI** | Rate Limit (429) | Exponential Backoff (Retry 3x) | "AI is busy, retrying..." |
| **Gemini AI** | Content Filter | Return specific error code | "Content filtered for safety." |
| **File Parser** | Corrupt PDF | Abort parsing | "File appears corrupted." |
| **Backend** | Timeout (504) | Client-side timeout (30s) | "Processing took too long." |

---

## 8. Database Interaction Strategy

The application employs a hybrid data strategy, utilizing **Firebase Firestore** for structured metadata and analysis results, and **Google Drive** for raw file storage/backup. This ensures fast application performance while leveraging the user's personal cloud storage for large files.

### 8.1. Data Persistence Models

#### **Firestore (Document Store)**
Acts as the primary source of truth for the application state. It stores:
- File Metadata (Name, Size, Type)
- Processing Status (`processing`, `processed`, `error`)
- AI Generated Content (Summary, Key Takeaways, Quiz Data)
- Sync Status with Google Drive

#### **Google Drive (Blob Store)**
Used for persistent storage of the original raw files (PDFs, DOCX, etc.). This avoids high bandwidth costs on our end and gives users ownership of their data.

### 8.2. Write Operations: The "Upload Transaction"

The upload process is a complex multi-step transaction that ensures data consistency across the Client, Google Drive, Backend AI, and Firestore.

```mermaid
sequenceDiagram
    participant Client as Dashboard UI
    participant Drive as Google Drive API
    participant AI as Python Backend
    participant DB as Firestore

    Client->>Client: User Selects File
    par Parallel Execution
        Client->>Drive: Upload File (Multipart)
        Drive-->>Client: Return `{ fileId: "123..." }`
    and
        Client->>AI: POST /process (File Blob)
        AI-->>Client: Return `{ data: Analysis, text: "..." }`
    end
    
    Client->>Client: Await both promises
    
    alt Success
        Client->>DB: addDoc('users/{uid}/documents')
        note right of DB: {<br/>  name: "notes.pdf",<br/>  driveId: "123...",<br/>  parsedData: {...},<br/>  status: "processed"<br/>}
        DB-->>Client: Return DocumentReference
    else Failure (AI or Drive)
        Client->>Client: Show Error Toast
        note left of Client: Does not write incomplete<br/>state to DB to avoid "zombie" records
    end
```

### 8.3. Read Operations: Real-time Synchronization

The dashboard relies on efficient querying to load user content.

```mermaid
sequenceDiagram
    participant Client as Dashboard UI
    participant DB as Firestore
    participant Drive as Google Drive

    Client->>DB: query('users/{uid}/documents', orderBy('createdAt', 'desc'))
    DB-->>Client: Return Snapshot [DocA, DocB, DocC]
    
    loop For Each Document
        Client->>Client: Render Card
        alt Status == 'processed'
            Client->>Client: Show Green Badge & Mastery
        else Status == 'processing'
            Client->>Client: Show Spinner
        end
    end
    
    note right of Client: Reading content happens<br/>when user clicks a specific card.
    
    Client->>Client: User clicks DocA
    Client->>Client: Navigate to /dashboard/files/{docId}
    Client->>DB: getDoc('users/{uid}/documents/{docId}')
    DB-->>Client: Return Full Analysis Data
```
