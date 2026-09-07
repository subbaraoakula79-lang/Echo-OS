/**
 * ECHO OS — Task Panel
 * Task management with CRUD operations.
 */

import { useState, useEffect } from 'react';
import { Plus, Check, Trash2, Clock, AlertTriangle } from 'lucide-react';
import { useTaskStore, type Task } from '../stores/task-store';

const PRIORITY_COLORS: Record<string, string> = {
  low: '#00ff88',
  medium: '#ffd700',
  high: '#ff5e00',
  urgent: '#ff0044',
};

export default function TaskPanel() {
  const { tasks, isLoading, loadTasks, addTask, completeTask, removeTask } = useTaskStore();
  const [newTitle, setNewTitle] = useState('');
  const [newPriority, setNewPriority] = useState('medium');

  useEffect(() => {
    loadTasks();
  }, []);

  const handleAdd = async () => {
    if (!newTitle.trim()) return;
    await addTask(newTitle, '', newPriority);
    setNewTitle('');
  };

  const pending = tasks.filter((t) => t.status !== 'completed');
  const completed = tasks.filter((t) => t.status === 'completed');

  return (
    <div className="flex flex-col h-full px-6 py-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-[11px] font-mono tracking-[3px] text-echo-orange font-bold">◈ TASK ENGINE</div>
          <div className="text-[9px] text-white/25 mt-1">{pending.length} active · {completed.length} completed</div>
        </div>
      </div>

      {/* Add Task */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          placeholder="New task..."
          className="flex-1 bg-white/[0.03] border border-echo-orange/10 rounded-lg px-3 py-2 text-[12px] text-white outline-none focus:border-echo-orange/30 placeholder:text-white/20"
        />
        <select
          value={newPriority}
          onChange={(e) => setNewPriority(e.target.value)}
          className="bg-white/[0.03] border border-echo-orange/10 rounded-lg px-2 py-2 text-[10px] text-white/60 outline-none"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
        <button
          onClick={handleAdd}
          className="w-9 h-9 rounded-lg bg-echo-orange/15 border border-echo-orange/25 flex items-center justify-center text-echo-orange hover:bg-echo-orange/25 transition-all"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto space-y-1.5 echo-scrollbar">
        {pending.map((task) => (
          <div key={task.id} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.05] hover:border-echo-orange/15 transition-all group">
            <button
              onClick={() => completeTask(task.id)}
              className="w-5 h-5 rounded border border-white/15 flex items-center justify-center hover:border-echo-gold hover:bg-echo-gold/10 transition-all"
            >
              <Check size={10} className="text-white/0 group-hover:text-echo-gold" />
            </button>
            <div className="flex-1 min-w-0">
              <div className="text-[12px] text-white/70 truncate">{task.title}</div>
              {task.due_date && (
                <div className="flex items-center gap-1 mt-0.5">
                  <Clock size={8} className="text-white/25" />
                  <span className="text-[9px] text-white/25">{new Date(task.due_date).toLocaleDateString()}</span>
                </div>
              )}
            </div>
            <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: PRIORITY_COLORS[task.priority] || '#ffd700', boxShadow: `0 0 4px ${PRIORITY_COLORS[task.priority] || '#ffd700'}` }} />
            <button
              onClick={() => removeTask(task.id)}
              className="opacity-0 group-hover:opacity-100 text-white/20 hover:text-red-400 transition-all"
            >
              <Trash2 size={12} />
            </button>
          </div>
        ))}

        {completed.length > 0 && (
          <>
            <div className="text-[8px] text-white/20 font-mono tracking-[2px] mt-4 mb-2">COMPLETED</div>
            {completed.slice(0, 5).map((task) => (
              <div key={task.id} className="flex items-center gap-3 p-2 rounded-lg opacity-40">
                <div className="w-5 h-5 rounded border border-echo-gold/30 bg-echo-gold/10 flex items-center justify-center">
                  <Check size={10} className="text-echo-gold" />
                </div>
                <div className="text-[11px] text-white/30 line-through truncate">{task.title}</div>
              </div>
            ))}
          </>
        )}

        {tasks.length === 0 && !isLoading && (
          <div className="text-center py-12 text-white/15 text-[12px]">No tasks yet. Add one above or ask ECHO.</div>
        )}
      </div>
    </div>
  );
}
