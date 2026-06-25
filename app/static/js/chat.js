function ragChat() {
  return {
    question: '',
    loading: false,
    messages: [
      {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: 'Upload PDFs, then ask a question. I will answer from your notes.',
        sources: []
      }
    ],
    async ask() {
      const text = this.question.trim();
      if (!text || this.loading) return;
      this.messages.push({ id: crypto.randomUUID(), role: 'user', text, sources: [] });
      this.question = '';
      this.loading = true;
      try {
        const response = await fetch('/chat/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: text })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Request failed.');
        this.messages.push({
          id: crypto.randomUUID(),
          role: 'assistant',
          text: data.answer,
          sources: data.sources || [],
          chatLogId: data.chat_log_id
        });
      } catch (error) {
        this.messages.push({
          id: crypto.randomUUID(),
          role: 'assistant',
          text: error.message,
          sources: []
        });
      } finally {
        this.loading = false;
        this.$nextTick(() => {
          const box = document.getElementById('messages');
          box.scrollTop = box.scrollHeight;
        });
      }
    },
    async sendFeedback(chatLogId, rating) {
      await fetch('/chat/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_log_id: chatLogId, rating })
      });
    }
  };
}
