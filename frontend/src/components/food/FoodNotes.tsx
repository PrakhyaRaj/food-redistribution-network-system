import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface FoodNote {
  _id: string;
  food_id: number;  // Changed to number
  note_type: string;
  content: string;
  metadata: {
    priority: 'high' | 'medium' | 'low';
    tags?: string[];
  };
  created_at: string;
}

interface FoodNotesProps {
  foodId: number;  // Changed to number
}

export const FoodNotes: React.FC<FoodNotesProps> = ({ foodId }) => {
  const [notes, setNotes] = useState<FoodNote[]>([]);
  const [newNote, setNewNote] = useState({
    type: 'quality',
    content: '',
    priority: 'medium' as 'high' | 'medium' | 'low'
  });
  const [adding, setAdding] = useState(false);
  const [loading, setLoading] = useState(true);

  // Quick-pick common notes for faster entry
  const commonNotes = [
    { label: "Contains nuts", type: "allergy", priority: "high" as const, text: "Contains nuts" },
    { label: "Spicy food", type: "handling", priority: "medium" as const, text: "Spicy food" },
    { label: "Keep refrigerated", type: "storage", priority: "high" as const, text: "Keep refrigerated" },
    { label: "Cooked today at 2 PM", type: "quality", priority: "medium" as const, text: "Cooked today at 2 PM" },
  ];

  useEffect(() => {
    loadNotes();
  }, [foodId]);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const data = await api.mongodb.getFoodNotes(foodId); // FIXED: Use mongodb.getFoodNotes
      setNotes(data.notes || data || []);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const addNote = async () => {
    if (!newNote.content.trim()) return;

    setAdding(true);
    try {
      await api.mongodb.addFoodNote(foodId, { // FIXED: Use mongodb.addFoodNote
        note_type: newNote.type,
        content: newNote.content,
        metadata: { priority: newNote.priority }
      });
      loadNotes();
      setNewNote({
        type: 'quality',
        content: '',
        priority: 'medium'
      });
    } catch (error) {
      console.error('Failed to add note:', error);
    } finally {
      setAdding(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">📝</span> Food Notes
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Add Note Form */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Select
              value={newNote.type}
              onValueChange={(value) => setNewNote({ ...newNote, type: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Note type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="quality">Quality</SelectItem>
                <SelectItem value="storage">Storage</SelectItem>
                <SelectItem value="handling">Handling</SelectItem>
                <SelectItem value="allergy">Allergy Info</SelectItem>
              </SelectContent>
            </Select>
            
            <Select
              value={newNote.priority}
              onValueChange={(value: 'high' | 'medium' | 'low') => 
                setNewNote({ ...newNote, priority: value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <Textarea
            placeholder="Note content..."
            value={newNote.content}
            onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
            rows={3}
          />

          {/* Quick add chips for common notes */}
          <div className="flex flex-wrap gap-2 text-xs">
            {commonNotes.map((n, idx) => (
              <Button
                key={idx}
                type="button"
                variant="outline"
                size="sm"
                className="h-8"
                onClick={() => setNewNote({ type: n.type, content: n.text, priority: n.priority })}
              >
                {n.label}
              </Button>
            ))}
          </div>
          
          <Button 
            onClick={addNote} 
            disabled={!newNote.content.trim() || adding || loading}
            className="w-full"
          >
            {adding ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Adding...
              </>
            ) : 'Add Note'}
          </Button>
        </div>

        {/* Notes List */}
        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        ) : notes.length > 0 ? (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {notes.map((note) => (
              <div 
                key={note._id}
                className={`p-4 border-l-4 rounded ${getPriorityColor(note.metadata.priority)}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="secondary" className="capitalize">
                    {note.note_type}
                  </Badge>
                  <Badge className={`capitalize ${
                    note.metadata.priority === 'high' ? 'bg-red-500' :
                    note.metadata.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}>
                    {note.metadata.priority}
                  </Badge>
                </div>
                <p className="mb-2 whitespace-pre-wrap">{note.content}</p>
                <p className="text-sm text-gray-500">
                  {new Date(note.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500 py-4">No notes added yet.</p>
        )}
      </CardContent>
    </Card>
  );
};