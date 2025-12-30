import React, { useState } from 'react';
import { MongoDBCard } from './MongoDBCard';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface FoodNote {
  _id: string;
  food_id: string;
  note_type: string;
  content: string;
  tags: string[];
  metadata: {
    priority: 'high' | 'medium' | 'low';
  };
  created_at: string;
  created_by: string;
}

const API_BASE = "http://127.0.0.1:5000";

const getHeaders = () => {
  const token = localStorage.getItem("token") || localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

interface FoodNotesManagerProps {
  foodId: number;
}

export const FoodNotesManager: React.FC<FoodNotesManagerProps> = ({ foodId }) => {
  const [notes, setNotes] = useState<FoodNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [noteType, setNoteType] = useState<'storage' | 'recipe' | 'warning' | 'other'>(
    'storage'
  );
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [submitting, setSubmitting] = useState(false);

  React.useEffect(() => {
    loadNotes();
  }, [foodId]);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE}/api/notes/food/${foodId}`,
        { headers: getHeaders() }
      );

      if (response.ok) {
        const data = await response.json();
        setNotes(data.notes || []);
      }
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    try {
      setSubmitting(true);
      const response = await fetch(
        `${API_BASE}/api/notes/food/${foodId}`,
        {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({
            note_type: noteType,
            content: newNote,
            metadata: { priority },
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setNotes([data.note, ...notes]);
        setNewNote('');
        setNoteType('storage');
        setPriority('medium');
      }
    } catch (error) {
      console.error('Failed to add note:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  const getNoteTypeIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'storage':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'recipe':
        return <FileText className="h-4 w-4 text-green-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <MongoDBCard title={`Food Notes (ID: ${foodId})`} icon="📝">
      {/* Add Note Form */}
      <form onSubmit={handleAddNote} className="mb-4 p-3 bg-gray-50 rounded-lg border">
        <div className="space-y-3">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Add a note about this food..."
            className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />

          <div className="grid grid-cols-3 gap-2">
            <select
              value={noteType}
              onChange={(e) => setNoteType(e.target.value as any)}
              className="px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="storage">Storage</option>
              <option value="recipe">Recipe</option>
              <option value="warning">Warning</option>
              <option value="other">Other</option>
            </select>

            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as any)}
              className="px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>

            <Button
              type="submit"
              disabled={submitting || !newNote.trim()}
              size="sm"
              className="w-full"
            >
              {submitting ? 'Adding...' : 'Add Note'}
            </Button>
          </div>
        </div>
      </form>

      {/* Notes List */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : notes.length > 0 ? (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {notes.map((note) => (
            <div
              key={note._id}
              className="p-3 border rounded-lg bg-white hover:shadow-sm transition"
            >
              <div className="flex items-start gap-3 mb-2">
                <div className="mt-1">{getNoteTypeIcon(note.note_type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge className={getPriorityColor(note.metadata.priority)}>
                      {note.metadata.priority}
                    </Badge>
                    <Badge variant="outline" className="capitalize text-xs">
                      {note.note_type}
                    </Badge>
                  </div>
                </div>
              </div>
              <p className="text-sm text-gray-700 mb-2">{note.content}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <p>By: {note.created_by}</p>
                <p>{new Date(note.created_at).toLocaleDateString()}</p>
              </div>
              {note.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {note.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      #{tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">No notes yet</p>
          <p className="text-sm text-gray-400 mt-1">
            Add notes to help others with this food
          </p>
        </div>
      )}
    </MongoDBCard>
  );
};
