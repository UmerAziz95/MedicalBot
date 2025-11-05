"""
HTML Template for the web application - Futuristic AI Chat Bot UI with improved file uploads
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedIntelligence AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0B66C2;
            --primary-dark: #0a4e95;
            --primary-light: #e6f0fa;
            --secondary: #6c757d;
            --light: #f8f9fa;
            --dark: #212529;
            --success: #28a745;
            --info: #17a2b8;
            --warning: #ffc107;
            --danger: #dc3545;
            --border-radius: 12px;
            --sidebar-width: 280px;
            --sidebar-collapsed-width: 70px;
            --chat-bg: #f0f2f5;
            --user-msg-bg: #0B66C2;
            --user-msg-text: #ffffff;
            --bot-msg-bg: #ffffff;
            --bot-msg-text: #212529;
            --header-height: 60px;
            --footer-height: 100px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--chat-bg);
            color: var(--dark);
            height: 100vh;
            overflow: hidden;
        }
        
        /* Main Layout */
        .app-container {
            display: flex;
            height: 100vh;
            width: 100%;
            overflow: hidden;
            position: relative;
        }
        
        /* Sidebar */
        .sidebar {
            width: var(--sidebar-width);
            background: linear-gradient(180deg, #051937, #004d7a);
            color: #fff;
            height: 100%;
            transition: all 0.3s;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 20px;
            z-index: 100;
        }
        
        .sidebar-collapsed {
            width: var(--sidebar-collapsed-width);
        }
        
        .sidebar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .app-logo {
            font-size: 22px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }
        
        .app-logo i {
            margin-right: 10px;
            font-size: 24px;
            color: #5cffb1;
        }
        
        .toggle-sidebar {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: #fff;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .toggle-sidebar:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .section-title {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 25px 0 10px;
            opacity: 0.8;
        }
        
        /* System Status Section */
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: var(--border-radius);
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .status-item i {
            margin-right: 8px;
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            margin-top: 5px;
        }
        
        .status-badge.success {
            background: rgba(40, 167, 69, 0.2);
            color: #5cffb1;
        }
        
        .status-badge.danger {
            background: rgba(220, 53, 69, 0.2);
            color: #ff8c8c;
        }
        
        /* File Upload Section */
        .file-drop-zone {
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: var(--border-radius);
            padding: 20px 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            background: rgba(255, 255, 255, 0.05);
        }
        
        .file-drop-zone:hover {
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.1);
        }
        
        .file-drop-zone i {
            font-size: 32px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 10px;
        }
        
        .file-info {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        /* Document List */
        .document-list {
            margin-top: 10px;
        }
        
        .document-item {
            display: flex;
            align-items: center;
            padding: 8px 5px;
            font-size: 13px;
            border-radius: 6px;
        }
        
        .document-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .document-item i {
            margin-right: 8px;
            opacity: 0.8;
        }
        
        /* Main Chat Area */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
        }
        
        /* Chat Header */
        .chat-header {
            height: var(--header-height);
            background: #ffffff;
            display: flex;
            align-items: center;
            padding: 0 20px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            z-index: 10;
        }
        
        .chat-title {
            font-weight: 600;
            font-size: 18px;
            margin: 0;
        }
        
        .header-subtitle {
            font-size: 13px;
            color: var(--secondary);
            margin: 0;
        }
        
        /* Chat Messages Area */
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            scroll-behavior: smooth;
        }
        
        .message {
            display: flex;
            margin-bottom: 20px;
            max-width: 85%;
        }
        
        .message.user-message {
            margin-left: auto;
            justify-content: flex-end;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 12px;
            background-color: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .message-avatar.user {
            background: var(--primary);
            color: white;
            order: 2;
            margin-right: 0;
            margin-left: 12px;
        }
        
        .message-avatar.bot {
            background: #4f67ab;
            color: white;
        }
        
        .message-content {
            padding: 12px 16px;
            border-radius: 18px;
            position: relative;
            max-width: 85%;
        }
        
        .user-message .message-content {
            background: var(--user-msg-bg);
            color: var(--user-msg-text);
            border-bottom-right-radius: 5px;
        }
        
        .bot-message .message-content {
            background: var(--bot-msg-bg);
            color: var(--bot-msg-text);
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        .message-text {
            font-size: 15px;
            line-height: 1.5;
            word-break: break-word;
        }
        
        .message-time {
            font-size: 11px;
            margin-top: 5px;
            opacity: 0.7;
            text-align: right;
        }
        
        .message-metadata {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .bot-message .message-metadata {
            color: rgba(0, 0, 0, 0.5);
        }
        
        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            padding: 12px 16px;
            background: var(--bot-msg-bg);
            border-radius: 18px;
            align-items: center;
            margin-bottom: 20px;
            max-width: 100px;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--secondary);
            border-radius: 50%;
            margin: 0 2px;
            animation: typingAnimation 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) {
            animation-delay: 0s;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typingAnimation {
            0% {
                transform: translateY(0px);
                opacity: 0.5;
            }
            50% {
                transform: translateY(-5px);
                opacity: 1;
            }
            100% {
                transform: translateY(0px);
                opacity: 0.5;
            }
        }
        
        /* Markdown Styling */
        .markdown {
            line-height: 1.6;
        }
        
        .markdown p {
            margin-bottom: 12px;
        }
        
        .markdown ul, .markdown ol {
            margin-bottom: 12px;
            padding-left: 20px;
        }
        
        .markdown h1, .markdown h2, .markdown h3 {
            margin-top: 16px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .markdown pre {
            background: rgba(0, 0, 0, 0.05);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 12px;
            overflow-x: auto;
        }
        
        .markdown code {
            background: rgba(0, 0, 0, 0.05);
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        
        .markdown blockquote {
            border-left: 3px solid var(--primary);
            padding-left: 10px;
            color: var(--secondary);
            margin: 0 0 12px;
        }
        
        /* Chat Input Area */
        .chat-input-container {
            background: #ffffff;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            padding: 15px 20px;
            position: relative;
            z-index: 10;
        }
        
        /* Enhanced File Upload Preview */
        .uploaded-file-container {
            margin-bottom: 10px;
        }
        
        .uploaded-file {
            display: flex;
            align-items: center;
            background: var(--primary-light);
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 13px;
            border: 1px solid rgba(11, 102, 194, 0.2);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .uploaded-file i {
            margin-right: 8px;
            font-size: 16px;
            color: var(--primary);
        }
        
        .uploaded-file-name {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-weight: 500;
        }
        
        .uploaded-file-size {
            color: var(--secondary);
            font-size: 11px;
            margin-left: 5px;
        }
        
        .uploaded-file-remove {
            background: transparent;
            border: none;
            color: var(--danger);
            cursor: pointer;
            padding: 0 5px;
            font-size: 16px;
            margin-left: 8px;
            transition: all 0.2s;
        }
        
        .uploaded-file-remove:hover {
            color: #b71c1c;
            transform: scale(1.1);
        }
        
        /* Chat Input Wrapper */
        .chat-input-wrapper {
            display: flex;
            align-items: center;
            background: var(--chat-bg);
            border-radius: 24px;
            padding: 0 5px 0 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }
        
        .chat-input-wrapper:focus-within {
            box-shadow: 0 2px 10px rgba(11, 102, 194, 0.15);
            border-color: rgba(11, 102, 194, 0.3);
        }
        
        .chat-input {
            flex: 1;
            border: none;
            padding: 10px 0;
            background: transparent;
            outline: none;
            font-size: 15px;
            resize: none;
            max-height: 100px;
            min-height: 24px;
        }
        
        .chat-input::placeholder {
            color: var(--secondary);
        }
        
        .chat-input-actions {
            display: flex;
            align-items: center;
        }
        
        .input-action-btn {
            background: transparent;
            border: none;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border-radius: 50%;
            color: var(--secondary);
            transition: all 0.2s;
            position: relative;
        }
        
        .input-action-btn:hover {
            background: rgba(0, 0, 0, 0.05);
            color: var(--primary);
        }
        
        .input-action-btn.active {
            color: var(--primary);
            background: rgba(11, 102, 194, 0.1);
        }
        
        .upload-btn-dot {
            position: absolute;
            width: 8px;
            height: 8px;
            background-color: var(--primary);
            border-radius: 50%;
            top: 8px;
            right: 8px;
            display: none;
        }
        
        .upload-active .upload-btn-dot {
            display: block;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.2);
                opacity: 0.8;
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .send-btn {
            background: var(--primary);
            color: #fff;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border: none;
            margin-left: 5px;
            transition: all 0.2s;
        }
        
        .send-btn:hover {
            background: var(--primary-dark);
            transform: scale(1.05);
        }
        
        .send-btn:disabled {
            background: var(--secondary);
            cursor: not-allowed;
            transform: none;
        }
        
        /* Response Type Selector */
        .response-type-selector {
            position: relative;
            margin-right: 8px;
        }
        
        .response-type-dropdown {
            position: absolute;
            bottom: 100%;
            right: 0;
            width: 180px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 10px 0;
            margin-bottom: 10px;
            display: none;
            z-index: 100;
            animation: fadeInUp 0.2s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translate3d(0, 10px, 0);
            }
            to {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }
        }
        
        .response-type-option {
            padding: 8px 15px;
            cursor: pointer;
            display: flex;
            align-items: center;
            transition: all 0.2s;
        }
        
        .response-type-option:hover {
            background: rgba(0, 0, 0, 0.05);
        }
        
        .response-type-option.selected {
            background: rgba(11, 102, 194, 0.1);
            color: var(--primary);
            font-weight: 500;
        }
        
        .response-type-option i {
            margin-right: 8px;
            font-size: 14px;
        }
        
        /* Welcome Message Animation */
        .welcome-message {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* File Upload Elements */
        .file-input {
            display: none;
        }
        
        /* Loading Spinner */
        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
            margin-right: 5px;
        }
        
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 0, 0, 0.3);
        }
        
        /* Responsive Adjustments */
        @media (max-width: 768px) {
            .sidebar {
                position: absolute;
                left: -280px;
                height: 100%;
                z-index: 1000;
            }
            
            .sidebar.active {
                left: 0;
            }
            
            .chat-container {
                width: 100%;
            }
            
            .toggle-sidebar {
                position: absolute;
                right: -40px;
                top: 10px;
                background: var(--primary);
            }
            
            .chat-header {
                padding-left: 15px;
            }
            
            .message {
                max-width: 90%;
            }
            
            .open-sidebar-btn {
                display: block;
            }
        }
        
        
        /* Voice UI Elements */
        .play-voice-btn {
            background: transparent;
            border: none;
            color: var(--primary);
            cursor: pointer;
            padding: 2px 5px;
            border-radius: 50%;
            transition: all 0.2s;
            font-size: 12px;
            margin-left: 5px;
        }

        .play-voice-btn:hover {
            background: rgba(11, 102, 194, 0.1);
            color: var(--primary-dark);
        }

        .play-voice-btn.playing {
            color: #d32f2f;
            animation: pulse 1.5s infinite;
        }

        #voice-btn {
            background: transparent;
            border: none;
            color: var(--secondary);
            transition: all 0.2s;
        }

        #voice-btn:hover, #voice-btn.active {
            color: var(--primary);
        }

        #voice-btn.listening {
            color: #d32f2f;
            animation: pulse 1.5s infinite;
        }

        #auto-play-btn {
            background: transparent;
            border: none;
            color: var(--secondary);
            transition: all 0.2s;
        }

        #auto-play-btn:hover, #auto-play-btn.active {
            color: var(--primary);
        }

        /* Audio controls */
        .audio-controls {
            display: flex;
            align-items: center;
            margin-top: 5px;
        }

        .volume-slider {
            width: 60px;
            height: 4px;
            margin: 0 5px;
            -webkit-appearance: none;
            appearance: none;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 2px;
            outline: none;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .volume-control:hover .volume-slider {
            opacity: 1;
        }

        .volume-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
        }

        .volume-slider::-moz-range-thumb {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
        }

        .volume-control {
            display: flex;
            align-items: center;
            margin-left: 8px;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <div class="app-logo">
                    <i class="fas fa-brain"></i>
                    <span class="logo-text">MedIntelligence</span>
                </div>
                <button class="toggle-sidebar" id="toggle-sidebar">
                    <i class="fas fa-bars"></i>
                </button>
            </div>
            
            <div class="section-title">System Status</div>
            <div class="status-card" id="system-status">
                <div class="status-item">
                    <i class="fas fa-plug"></i>
                    <span>Checking connection...</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-database"></i>
                    <span>Loading document count...</span>
                </div>
            </div>
            
            <div class="section-title">Upload Document</div>
            <div class="file-drop-zone" id="sidebar-file-drop">
                <i class="fas fa-cloud-upload-alt"></i>
                <div>Drag & drop or click to upload</div>
                <div class="file-info">Supports PDF, PNG, JPG</div>
                <input type="file" id="sidebar-file-input" class="file-input">
            </div>
            
            <div class="section-title">Documents</div>
            <div class="document-list" id="document-list">
                <div class="document-item">
                    <i class="fas fa-file-pdf"></i>
                    <span>Loading documents...</span>
                </div>
            </div>
            
            <div class="section-title">About</div>
            <p style="font-size: 13px; opacity: 0.8;">
                This Medical RAG system helps you get accurate answers from your medical documents using advanced AI.
            </p>
        </div>

        <!-- Main Chat Container -->
        <div class="chat-container">
            <!-- Chat Header -->
            <div class="chat-header">
                <div>
                    <h1 class="chat-title">Medical Assistant</h1>
                    <p class="header-subtitle">Ask questions about your medical documents</p>
                </div>
            </div>
            
            <!-- Messages Container -->
            <div class="messages-container" id="messages-container">
                <!-- Welcome Message -->
                <div class="message bot-message welcome-message">
                    <div class="message-avatar bot">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">
                            <strong>Welcome to MedIntelligence!</strong>
                            <p>I'm your AI medical assistant. I can help answer questions based on your medical documents. You can:</p>
                            <ul>
                                <li>Ask specific questions about medical topics</li>
                                <li>Upload documents for analysis</li>
                                <li>Choose different response types for varied detail levels</li>
                                <li>Use voice input by clicking the microphone icon</li>
                                <li>Listen to responses by clicking the play button</li>
                            </ul>
                            <p>How can I assist you today?</p>
                        </div>
                        <div class="message-time">Just now</div>
                    </div>
                </div>
            </div>
            
            <!-- Chat Input Area -->
            <div class="chat-input-container">
                <!-- File Upload Preview - Now separated from the input -->
                <div id="uploaded-file-container" class="uploaded-file-container"></div>
                
                <div class="chat-input-wrapper">
                    <textarea class="chat-input" id="chat-input" placeholder="Type your medical question here..." rows="1"></textarea>
                    <div class="chat-input-actions">
                        <div class="response-type-selector">
                            <button class="input-action-btn" id="response-type-btn" title="Response Type">
                                <i class="fas fa-sliders-h"></i>
                            </button>
                            <div class="response-type-dropdown" id="response-type-dropdown">
                                <div class="response-type-option selected" data-type="medical">
                                    <i class="fas fa-notes-medical"></i> Medical
                                </div>
                                <div class="response-type-option" data-type="basic">
                                    <i class="fas fa-align-left"></i> Basic
                                </div>
                                <div class="response-type-option" data-type="detailed">
                                    <i class="fas fa-file-alt"></i> Detailed
                                </div>
                            </div>
                        </div>
                        <button class="input-action-btn" id="voice-btn" title="Voice Input">
                            <i class="fas fa-microphone"></i>
                        </button>
                        <button class="input-action-btn" id="auto-play-btn" title="Auto-play Responses: OFF">
                            <i class="fas fa-volume-up"></i>
                        </button>
                        <button class="input-action-btn" id="upload-btn" title="Upload File">
                            <i class="fas fa-paperclip"></i>
                            <span class="upload-btn-dot"></span>
                        </button>
                        <input type="file" id="chat-file-input" class="file-input">
                        <button class="send-btn" id="send-btn" disabled>
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // DOM Elements
            const sidebar = document.getElementById('sidebar');
            const toggleSidebarBtn = document.getElementById('toggle-sidebar');
            const messagesContainer = document.getElementById('messages-container');
            const chatInput = document.getElementById('chat-input');
            const sendBtn = document.getElementById('send-btn');
            const sidebarFileInput = document.getElementById('sidebar-file-input');
            const chatFileInput = document.getElementById('chat-file-input');
            const sidebarFileDropZone = document.getElementById('sidebar-file-drop');
            const uploadBtn = document.getElementById('upload-btn');
            const uploadedFileContainer = document.getElementById('uploaded-file-container');
            const responseTypeBtn = document.getElementById('response-type-btn');
            const responseTypeDropdown = document.getElementById('response-type-dropdown');
            const systemStatus = document.getElementById('system-status');
            const documentList = document.getElementById('document-list');
            const voiceBtn = document.getElementById('voice-btn');
            const autoPlayBtn = document.getElementById('auto-play-btn');
            
            
            // State
            let uploadedFile = null;
            let currentResponseType = 'medical';
            let isTyping = false;
            let isListening = false;
            let recognition = null;
            let autoPlayResponses = false;
            
            // Audio state
            let currentAudio = null;
            let currentAudioButton = null; 
            let currentVolume = 0.7;
            
            // Initialize
            fetchSystemStatus();
            adjustTextareaHeight();
            setupSpeechRecognition();
            
            // Event Listeners
            toggleSidebarBtn.addEventListener('click', toggleSidebar);
            
            chatInput.addEventListener('input', function() {
                adjustTextareaHeight();
                updateSendButtonState();
            });
            
            chatInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (!sendBtn.disabled) {
                        handleSendMessage();
                    }
                }
            });
            
            sendBtn.addEventListener('click', handleSendMessage);
            
            // File upload event listeners - Sidebar
            sidebarFileDropZone.addEventListener('click', () => sidebarFileInput.click());
            sidebarFileDropZone.addEventListener('dragover', handleDragOver);
            sidebarFileDropZone.addEventListener('dragleave', handleDragLeave);
            sidebarFileDropZone.addEventListener('drop', handleFileDrop);
            sidebarFileInput.addEventListener('change', function() {
                if (this.files.length) {
                    handleFile(this.files[0], 'sidebar');
                }
            });
            
            // File upload event listeners - Chat
            uploadBtn.addEventListener('click', () => chatFileInput.click());
            chatFileInput.addEventListener('change', function() {
                if (this.files.length) {
                    handleFile(this.files[0], 'chat');
                }
            });
            
            // Response type dropdown
            responseTypeBtn.addEventListener('click', toggleResponseTypeDropdown);
            responseTypeDropdown.addEventListener('click', handleResponseTypeSelection);
            document.addEventListener('click', function(e) {
                if (!responseTypeBtn.contains(e.target) && !responseTypeDropdown.contains(e.target)) {
                    responseTypeDropdown.style.display = 'none';
                }
            });
            
            // Voice functionality
            if (voiceBtn) {
                voiceBtn.addEventListener('click', toggleSpeechRecognition);
            }
            
            if (autoPlayBtn) {
                autoPlayBtn.addEventListener('click', toggleAutoPlayResponses);
            }
            
            // Functions
            function toggleSidebar() {
                sidebar.classList.toggle('sidebar-collapsed');
                document.querySelectorAll('.logo-text, .section-title, .status-card, .file-drop-zone, .document-list, .sidebar p').forEach(el => {
                    el.style.display = sidebar.classList.contains('sidebar-collapsed') ? 'none' : '';
                });
            }
            
            function updateSendButtonState() {
                sendBtn.disabled = !chatInput.value.trim() && !uploadedFile;
            }
            
            function adjustTextareaHeight() {
                chatInput.style.height = 'auto';
                chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
            }
            
            function toggleResponseTypeDropdown(e) {
                e.stopPropagation();
                responseTypeDropdown.style.display = responseTypeDropdown.style.display === 'block' ? 'none' : 'block';
            }
            
            function handleResponseTypeSelection(e) {
                const option = e.target.closest('.response-type-option');
                if (option) {
                    currentResponseType = option.dataset.type;
                    document.querySelectorAll('.response-type-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    option.classList.add('selected');
                    responseTypeDropdown.style.display = 'none';
                }
            }
            
            function handleDragOver(e) {
                e.preventDefault();
                this.style.background = 'rgba(255, 255, 255, 0.1)';
                this.style.borderColor = 'rgba(255, 255, 255, 0.6)';
            }
            
            function handleDragLeave(e) {
                e.preventDefault();
                this.style.background = 'rgba(255, 255, 255, 0.05)';
                this.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            }
            
            function handleFileDrop(e) {
                e.preventDefault();
                this.style.background = 'rgba(255, 255, 255, 0.05)';
                this.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                
                if (e.dataTransfer.files.length) {
                    handleFile(e.dataTransfer.files[0], 'sidebar');
                }
            }
            
            function handleFile(file, source) {
                // Check file type
                const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/gif', 'image/bmp'];
                if (!validTypes.includes(file.type)) {
                    alert('Please upload a PDF or image file (PNG, JPG, GIF, BMP)');
                    return;
                }
                
                // Check file size (max 10MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('File size exceeds 10MB limit');
                    return;
                }
                
                // Set uploaded file and update UI
                uploadedFile = file;
                updateSendButtonState();
                
                // Update the upload button to show there's a file attached
                uploadBtn.classList.add('active');
                document.querySelector('.chat-input-wrapper').classList.add('upload-active');
                
                // Display file preview
                let fileIcon = 'fa-file-pdf';
                if (file.type.startsWith('image/')) {
                    fileIcon = 'fa-file-image';
                }
                
                // Always show the file in the chat input area regardless of where it was uploaded from
                uploadedFileContainer.innerHTML = `
                    <div class="uploaded-file">
                        <i class="fas ${fileIcon}"></i>
                        <div>
                            <span class="uploaded-file-name">${file.name}</span>
                            <span class="uploaded-file-size">${formatFileSize(file.size)}</span>
                        </div>
                        <button class="uploaded-file-remove" id="remove-file">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
                
                // Add remove event listener
                document.getElementById('remove-file').addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    clearFileUpload();
                });
            }
            
            function clearFileUpload() {
                uploadedFile = null;
                uploadedFileContainer.innerHTML = '';
                uploadBtn.classList.remove('active');
                document.querySelector('.chat-input-wrapper').classList.remove('upload-active');
                sidebarFileInput.value = '';
                chatFileInput.value = '';
                updateSendButtonState();
            }
            
            function handleSendMessage() {
                const question = chatInput.value.trim();
                
                // If no question and no file, do nothing
                if (!question && !uploadedFile) return;
                
                // Add user message to chat
                addUserMessage(question || 'Analyze this file');
                
                // Clear input and reset
                chatInput.value = '';
                adjustTextareaHeight();
                
                // Show typing indicator
                showTypingIndicator();
                
                // Prepare form data
                const formData = new FormData();
                formData.append('question', question);
                formData.append('prompt_type', currentResponseType);
                
                if (uploadedFile) {
                    formData.append('file', uploadedFile);
                }
                
                // Send API request
                fetch('/api/query', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(result => {
                    // Remove typing indicator
                    hideTypingIndicator();
                    
                    if (result.error) {
                        addBotErrorMessage(result.error);
                    } else {
                        addBotMessage(result.answer, result);
                    }
                    
                    // Clear file upload after sending
                    clearFileUpload();
                    updateSendButtonState();
                })
                .catch(error => {
                    hideTypingIndicator();
                    addBotErrorMessage('Network error. Please try again.');
                    console.error('Error:', error);
                });
                
                // Scroll to bottom
                scrollToBottom();
            }
            
            function addUserMessage(text) {
                // Add file info if it's a file upload
                let fileInfo = '';
                if (uploadedFile) {
                    const fileIcon = uploadedFile.type.startsWith('image/') ? 'fa-file-image' : 'fa-file-pdf';
                    fileInfo = `
                        <div style="margin-top: 8px; padding: 8px; background-color: rgba(255, 255, 255, 0.2); border-radius: 8px; font-size: 12px;">
                            <i class="fas ${fileIcon}"></i> ${uploadedFile.name} (${formatFileSize(uploadedFile.size)})
                        </div>
                    `;
                }
                
                const messageHtml = `
                    <div class="message user-message">
                        <div class="message-content">
                            <div class="message-text">${text}</div>
                            ${fileInfo}
                            <div class="message-time">${formatTime(new Date())}</div>
                        </div>
                        <div class="message-avatar user">
                            <i class="fas fa-user"></i>
                        </div>
                    </div>
                `;
                
                messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
                scrollToBottom();
            }
            
            function addBotMessage(text, data) {
               
                const renderedText = marked.parse(text);
                
                // Generate a unique ID for this message's audio
                const messageId = 'msg-' + Date.now();
                
                // Create a message with audio controls
                const messageHtml = `
                    <div class="message bot-message">
                        <div class="message-avatar bot">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            <div class="message-text markdown">${renderedText}</div>
                            <div class="message-metadata">
                                <span>${data.chunks_found || 0} chunks found</span>
                                <span>${data.query_time ? data.query_time.toFixed(2) + 's' : 'N/A'}</span>
                                <div class="audio-controls">
                                    <button class="play-voice-btn" id="${messageId}-play" data-text="${encodeURIComponent(text)}">
                                        <i class="fas fa-play"></i>
                                    </button>
                                    <div class="volume-control">
                                        <i class="fas fa-volume-up" id="${messageId}-volume-icon"></i>
                                        <input type="range" class="volume-slider" id="${messageId}-volume" min="0" max="1" step="0.1" value="${currentVolume}">
                                    </div>
                                </div>
                            </div>
                            <div class="message-time">${formatTime(new Date())}</div>
                        </div>
                    </div>
                `;
                
                messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
                
                // Add event listener to the play button
                const playBtn = document.getElementById(`${messageId}-play`);
                const volumeSlider = document.getElementById(`${messageId}-volume`);
                const volumeIcon = document.getElementById(`${messageId}-volume-icon`);
                
                if (playBtn) {
                    playBtn.addEventListener('click', function() {
                        const textToPlay = decodeURIComponent(this.dataset.text);
                        togglePlayVoice(textToPlay, this, messageId);
                    });
                }
                
                if (volumeSlider) {
                    volumeSlider.addEventListener('input', function() {
                        currentVolume = parseFloat(this.value);
                        updateVolumeIcon(volumeIcon, currentVolume);
                        
                        // Update current audio if playing
                        if (currentAudio) {
                            currentAudio.volume = currentVolume;
                        }
                    });
                    
                    // Initialize volume icon
                    updateVolumeIcon(volumeIcon, currentVolume);
                }
                
                scrollToBottom();
                
                // Auto-play if enabled
                if (autoPlayResponses) {
                    togglePlayVoice(text, playBtn, messageId);
                }
            }
            
            function updateVolumeIcon(iconElement, volume) {
                if (!iconElement) return;
                
                if (volume === 0) {
                    iconElement.className = 'fas fa-volume-mute';
                } else if (volume < 0.5) {
                    iconElement.className = 'fas fa-volume-down';
                } else {
                    iconElement.className = 'fas fa-volume-up';
                }
            }
            
           function togglePlayVoice(text, buttonElement, messageId) {
            if (!text) return;
            
            // Check if this is the currently playing button
            const isCurrentButton = buttonElement === currentAudioButton;
            
            // If there's already audio playing
            if (currentAudio) {
                // Pause the current audio
                currentAudio.pause();
                
                // Reset the previous button
                if (currentAudioButton) {
                    currentAudioButton.innerHTML = '<i class="fas fa-play"></i>';
                    currentAudioButton.classList.remove('playing');
                }
        
                // If the same button was clicked, just stop and return
                if (isCurrentButton) {
                    currentAudio = null;
                    currentAudioButton = null;
                    return;
                }
    }
    
    // Show loading indicator
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    buttonElement.disabled = true;
    
    // Set this as the current audio button
    currentAudioButton = buttonElement;
    
    // Call the TTS API
    fetch('/api/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            lang: 'en'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create audio element
            const audio = new Audio(`data:${data.audio_type};base64,${data.audio_data}`);
            audio.volume = currentVolume;
            
            // Set as current audio
            currentAudio = audio;
            
            // Update button to pause icon
            buttonElement.innerHTML = '<i class="fas fa-pause"></i>';
            buttonElement.disabled = false;
            buttonElement.classList.add('playing');
            
            // Play the audio
            audio.play();
            
            // When audio ends
            audio.onended = function() {
                if (buttonElement === currentAudioButton) {
                    buttonElement.innerHTML = '<i class="fas fa-play"></i>';
                    buttonElement.classList.remove('playing');
                    currentAudio = null;
                    currentAudioButton = null;
                }
            };
            
            // Remove existing onclick handler to prevent conflicts
            buttonElement.onclick = null;
            
            // Clean up existing event listeners
            const newButton = buttonElement.cloneNode(true);
            buttonElement.parentNode.replaceChild(newButton, buttonElement);
            
            // Add the proper event listener
            newButton.addEventListener('click', function() {
                // This handles future clicks after audio is loaded
                if (currentAudio === audio) {
                    if (audio.paused) {
                        audio.play();
                        this.innerHTML = '<i class="fas fa-pause"></i>';
                        this.classList.add('playing');
                    } else {
                        audio.pause();
                        this.innerHTML = '<i class="fas fa-play"></i>';
                        this.classList.remove('playing');
                    }
                } else {
                    // If this button is clicked again but it's no longer the current audio
                    togglePlayVoice(text, this, messageId);
                }
            });
            
            // Update reference to the new button
            currentAudioButton = newButton;
            
        } else {
            console.error('TTS Error:', data.error);
            buttonElement.innerHTML = '<i class="fas fa-play"></i>';
            buttonElement.disabled = false;
            currentAudioButton = null;
        }
    })
    .catch(error => {
        console.error('Error calling TTS API:', error);
        buttonElement.innerHTML = '<i class="fas fa-play"></i>';
        buttonElement.disabled = false;
        currentAudioButton = null;
    });
}
            
            function addBotErrorMessage(text) {
                const messageHtml = `
                    <div class="message bot-message">
                        <div class="message-avatar bot">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="message-content" style="background-color: #ffeaea; color: #d32f2f;">
                            <div class="message-text">
                                <strong>Error:</strong> ${text}
                            </div>
                            <div class="message-time">${formatTime(new Date())}</div>
                        </div>
                    </div>
                `;
                
                messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
                scrollToBottom();
            }
            
            function showTypingIndicator() {
                if (isTyping) return;
                isTyping = true;
                
                const typingHtml = `
                    <div class="message bot-message" id="typing-indicator">
                        <div class="message-avatar bot">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="typing-indicator">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    </div>
                `;
                
                messagesContainer.insertAdjacentHTML('beforeend', typingHtml);
                scrollToBottom();
            }
            
            function hideTypingIndicator() {
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
                isTyping = false;
            }
            
            function scrollToBottom() {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function formatTime(date) {
                const hours = date.getHours();
                const minutes = date.getMinutes();
                return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
            }
            
            function formatFileSize(bytes) {
                if (bytes < 1024) return bytes + ' bytes';
                else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
                else return (bytes / 1048576).toFixed(1) + ' MB';
            }
            
            async function fetchSystemStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    // Update system status
                    let statusHtml = '';
                    
                    if (data.api_connected) {
                        statusHtml += `
                            <div class="status-item">
                                <i class="fas fa-check-circle"></i>
                                <span>API Connected</span>
                                <div class="status-badge success">
                                    <i class="fas fa-plug"></i> Online
                                </div>
                            </div>
                        `;
                    } else {
                        statusHtml += `
                            <div class="status-item">
                                <i class="fas fa-exclamation-circle"></i>
                                <span>API Not Connected</span>
                                <div class="status-badge danger">
                                    <i class="fas fa-times"></i> Offline
                                </div>
                            </div>
                        `;
                    }
                    
                    statusHtml += `
                        <div class="status-item">
                            <i class="fas fa-database"></i>
                            <span>Documents: <strong>${data.document_count || 0}</strong></span>
                        </div>
                    `;
                    
                    systemStatus.innerHTML = statusHtml;
                    
                    // Update document list
                    let docListHtml = '';
                    
                    if (data.sources && data.sources.length) {
                        data.sources.forEach(source => {
                            docListHtml += `
                                <div class="document-item">
                                    <i class="fas fa-file-pdf"></i>
                                    <span>${source}</span>
                                </div>
                            `;
                        });
                    } else {
                        docListHtml = `
                            <div class="document-item">
                                <i class="fas fa-info-circle"></i>
                                <span>No documents loaded</span>
                            </div>
                        `;
                    }
                    
                    documentList.innerHTML = docListHtml;
                    
                } catch (error) {
                    console.error('Error fetching system status:', error);
                    systemStatus.innerHTML = `
                        <div class="status-item">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>Connection Error</span>
                            <div class="status-badge danger">
                                <i class="fas fa-times"></i> Offline
                            </div>
                        </div>
                    `;
                }
            }
            
            // Speech recognition setup
            function setupSpeechRecognition() {
                // Check if browser supports speech recognition
                if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = true;
                    recognition.lang = 'en-US';
                    
                    recognition.onstart = function() {
                        isListening = true;
                        voiceBtn.classList.add('listening');
                        voiceBtn.innerHTML = '<i class="fas fa-microphone-alt"></i>';
                        console.log('Speech recognition started');
                    };
                    
                    recognition.onresult = function(event) {
                        let interimTranscript = '';
                        let finalTranscript = '';
                        
                        for (let i = event.resultIndex; i < event.results.length; i++) {
                            const transcript = event.results[i][0].transcript;
                            if (event.results[i].isFinal) {
                                finalTranscript += transcript;
                            } else {
                                interimTranscript += transcript;
                            }
                        }
                        
                        // Update chat input with transcript
                        if (finalTranscript) {
                            chatInput.value = finalTranscript;
                            adjustTextareaHeight();
                            updateSendButtonState();
                        } else if (interimTranscript) {
                            chatInput.value = interimTranscript;
                            adjustTextareaHeight();
                        }
                    };
                    
                    recognition.onerror = function(event) {
                        isListening = false;
                        voiceBtn.classList.remove('listening');
                        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                        console.error('Speech recognition error', event.error);
                        
                        if (event.error === 'not-allowed') {
                            // Show a message to the user about microphone permission
                            addBotErrorMessage('Microphone access denied. Please allow microphone access to use voice input.');
                        }
                    };
                    
                    recognition.onend = function() {
                        isListening = false;
                        voiceBtn.classList.remove('listening');
                        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                        console.log('Speech recognition ended');
                    };
                    
                    return true;
                } else {
                    console.error('Speech recognition not supported by this browser');
                    return false;
                }
            }

            // Toggle speech recognition
            function toggleSpeechRecognition() {
                if (!recognition) {
                    const supported = setupSpeechRecognition();
                    if (!supported) {
                        addBotErrorMessage('Speech recognition is not supported by your browser');
                        return;
                    }
                }
                
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            }

            // Toggle auto-play responses
            function toggleAutoPlayResponses() {
                autoPlayResponses = !autoPlayResponses;
                
                if (autoPlayResponses) {
                    autoPlayBtn.classList.add('active');
                    autoPlayBtn.title = 'Auto-play responses: ON';
                } else {
                    autoPlayBtn.classList.remove('active');
                    autoPlayBtn.title = 'Auto-play responses: OFF';
                }
            }
        });
    </script>
</body>
</html>"""