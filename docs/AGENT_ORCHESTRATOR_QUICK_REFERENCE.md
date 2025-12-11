# Agent Orchestrator - Quick Reference

## Overview
The Agent Orchestrator provides centralized coordination for AI agents, managing task distribution, load balancing, and inter-agent communication.

## Core Services

### 1. Agent Orchestrator Service

**Import**:
```typescript
import { getOrchestratorService, LoadBalancingStrategy } from './services/agent-orchestrator-service';
```

**Initialize**:
```typescript
const orchestrator = getOrchestratorService(LoadBalancingStrategy.LEAST_LOADED);
orchestrator.start();
```

**Register Agent**:
```typescript
const agentId = orchestrator.registerAgent(agent, maxLoad);
```

**Submit Task**:
```typescript
const taskId = orchestrator.submitTask(task, maxRetries);
```

**Get Status**:
```typescript
const taskStatus = orchestrator.getTaskStatus(taskId);
const agentHealth = orchestrator.getAgentHealth(agentId);
const queueStats = orchestrator.getQueueStatistics();
```

### 2. Agent Communication Framework

**Import**:
```typescript
import { getCommunicationFramework } from './services/agent-communication-framework';
```

**Initialize**:
```typescript
const framework = getCommunicationFramework();
framework.start();
```

**Send Message**:
```typescript
const messageId = await framework.sendMessage(message, maxRetries);
```

**Broadcast**:
```typescript
const messageIds = await framework.broadcastMessage(
  fromAgentId,
  toAgentIds,
  messageType,
  payload
);
```

**Update State**:
```typescript
framework.updateAgentState(agentId, { status: 'busy', currentLoad: 5 });
```

**Request Collaboration**:
```typescript
const collaborationId = await framework.requestCollaboration(
  initiatorId,
  participantIds,
  task,
  aggregationConfig
);
```

## Load Balancing Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `ROUND_ROBIN` | Distribute evenly | Equal distribution |
| `LEAST_LOADED` | Assign to least busy | Optimize utilization |
| `CAPABILITY_MATCH` | Match by capability | Specialized tasks |
| `PRIORITY_BASED` | Based on task priority | Critical tasks first |

## Aggregation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `all` | Return all results | Need complete data |
| `first` | Return first result | Speed priority |
| `majority` | Most common result | Voting/consensus |
| `weighted` | Weighted average | Trust-based |

## Agent Status Values

- `available`: Ready for tasks
- `busy`: At max capacity
- `offline`: Not responding
- `error`: In error state

## Task Status Values

- `pending`: Waiting for assignment
- `assigned`: Assigned to agent
- `running`: Currently executing
- `completed`: Successfully finished
- `failed`: Execution failed
- `cancelled`: Manually cancelled

## Events

### Orchestrator Events:
- `started`: Service started
- `stopped`: Service stopped
- `agent-registered`: New agent registered
- `agent-unregistered`: Agent removed
- `agent-online`: Agent came online
- `agent-offline`: Agent went offline
- `task-submitted`: New task added
- `task-assigned`: Task assigned to agent
- `task-completed`: Task finished successfully
- `task-failed`: Task execution failed
- `task-reassigned`: Task moved to different agent

### Communication Events:
- `message-sent`: Message queued
- `message-delivered`: Message delivered
- `message-failed`: Message delivery failed
- `state-synchronized`: State updated
- `collaboration-started`: Collaboration initiated
- `collaboration-completed`: Collaboration finished
- `collaboration-cancelled`: Collaboration cancelled

## Dashboard Access

Navigate to `/orchestration` to view:
- Real-time agent status
- Task queue monitoring
- Performance metrics
- System statistics

## Common Patterns

### Pattern 1: Register and Monitor Agent
```typescript
const orchestrator = getOrchestratorService();
orchestrator.start();

const agentId = orchestrator.registerAgent(myAgent, 10);

orchestrator.on('agent-offline', (agent) => {
  console.log(`Agent ${agent.id} went offline`);
});

const health = orchestrator.getAgentHealth(agentId);
console.log(`Agent completed ${health.tasksCompleted} tasks`);
```

### Pattern 2: Submit High-Priority Task
```typescript
const taskId = orchestrator.submitTask({
  id: 'urgent-task',
  type: 'generate-test',
  priority: Priority.CRITICAL,
  data: { urgent: true },
  context: { userId: 'user-1', projectId: 'project-1' },
}, 5); // 5 retries

orchestrator.on('task-completed', ({ task, result }) => {
  console.log(`Task ${task.id} completed:`, result);
});
```

### Pattern 3: Multi-Agent Collaboration
```typescript
const framework = getCommunicationFramework();
framework.start();

const collaborationId = await framework.requestCollaboration(
  'orchestrator',
  ['agent-1', 'agent-2', 'agent-3'],
  { analyze: 'test-results' },
  {
    strategy: 'majority',
    timeout: 10000,
    minResponses: 2,
  }
);

framework.on('collaboration-completed', ({ collaboration, aggregatedResult }) => {
  console.log('Collaboration result:', aggregatedResult);
});
```

### Pattern 4: State Synchronization
```typescript
const framework = getCommunicationFramework();

// Update local agent state
framework.updateAgentState('agent-1', {
  status: 'busy',
  currentLoad: 8,
  metadata: { currentTask: 'test-generation' },
});

// Sync across all agents
await framework.synchronizeStates(['agent-1', 'agent-2', 'agent-3']);

// Monitor state changes
framework.on('state-synchronized', (event) => {
  console.log(`Agent ${event.agentId} state changed:`, event.currentState);
});
```

## Configuration

### Orchestrator Configuration:
```typescript
const orchestrator = new AgentOrchestratorService(
  LoadBalancingStrategy.LEAST_LOADED
);

// Heartbeat check interval: 30 seconds
// Task processing interval: 1 second
// Default max retries: 3
```

### Communication Configuration:
```typescript
const framework = new AgentCommunicationFramework();

// Message processing interval: 100ms
// Default max retries: 3
// Auto-cleanup: 1 hour old messages
```

## Troubleshooting

### Agent Not Receiving Tasks
1. Check agent status: `orchestrator.getAgent(agentId)`
2. Verify agent is registered: `orchestrator.getAllAgents()`
3. Check agent load: Ensure `currentLoad < maxLoad`
4. Verify heartbeat: Check `lastHeartbeat` timestamp

### Messages Not Delivering
1. Check message handler registered: `framework.registerMessageHandler()`
2. Verify message status: `framework.getMessageStatus(messageId)`
3. Check message statistics: `framework.getMessageStatistics()`
4. Review retry count vs max retries

### High Task Failure Rate
1. Review agent health metrics: `orchestrator.getAgentHealth()`
2. Check task retry configuration
3. Monitor agent error logs
4. Verify task timeout settings

## Performance Tips

1. **Use Appropriate Load Balancing**: Choose strategy based on workload
2. **Set Realistic Max Load**: Don't overload agents
3. **Monitor Health Metrics**: Track response times and failure rates
4. **Clean Up Old Data**: Regularly clear completed tasks and messages
5. **Use Collaboration Wisely**: Only when multiple perspectives needed
6. **Optimize Heartbeat Interval**: Balance between responsiveness and overhead

## API Reference

See full API documentation in:
- `src/services/agent-orchestrator-service.ts`
- `src/services/agent-communication-framework.ts`
- `frontend/src/components/Orchestration/OrchestrationDashboard.tsx`

## Support

For issues or questions:
1. Check agent logs
2. Review dashboard metrics
3. Verify configuration
4. Consult full documentation
