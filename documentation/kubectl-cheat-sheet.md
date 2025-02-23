Here's a concise `kubectl` cheat sheet to help with everyday tasks:

### **Cluster Info**
- **Get cluster info:**
  ```bash
  kubectl cluster-info
  ```
- **Get nodes in the cluster:**
  ```bash
  kubectl get nodes
  ```

### **Namespaces**
- **List namespaces:**
  ```bash
  kubectl get namespaces
  ```
- **Switch namespace:**
  ```bash
  kubectl config set-context --current --namespace=<namespace-name>
  ```

### **Pods**
- **List pods:**
  ```bash
  kubectl get pods
  ```
- **Get pods in all namespaces:**
  ```bash
  kubectl get pods --all-namespaces
  ```
- **Get detailed information about a pod:**
  ```bash
  kubectl describe pod <pod-name>
  ```
- **View pod logs:**
  ```bash
  kubectl logs <pod-name>
  ```
- **View logs of a specific container in a pod:**
  ```bash
  kubectl logs <pod-name> -c <container-name>
  ```
- **Get pod logs since a certain time:**
  ```bash
  kubectl logs <pod-name> --since=1h
  ```
- **Get all logs from all pods in a namespace:**
  ```bash
  kubectl logs -l app=<app-name> --all-containers=true
  ```

### **Deployments**
- **List deployments:**
  ```bash
  kubectl get deployments
  ```
- **Scale a deployment:**
  ```bash
  kubectl scale deployment <deployment-name> --replicas=<number-of-replicas>
  ```
- **Update a deployment:**
  ```bash
  kubectl set image deployment/<deployment-name> <container-name>=<new-image>
  ```
  
### **Services**
- **List services:**
  ```bash
  kubectl get services
  ```
- **Get detailed service info:**
  ```bash
  kubectl describe service <service-name>
  ```
- **Get service endpoint:**
  ```bash
  kubectl get svc <service-name> -o wide
  ```

### **ConfigMaps and Secrets**
- **Get ConfigMaps:**
  ```bash
  kubectl get configmaps
  ```
- **Get a specific ConfigMap:**
  ```bash
  kubectl describe configmap <configmap-name>
  ```
- **Get Secrets:**
  ```bash
  kubectl get secrets
  ```
- **Get a specific secret:**
  ```bash
  kubectl describe secret <secret-name>
  ```

### **Pods and Containers**
- **Execute a command in a running container:**
  ```bash
  kubectl exec -it <pod-name> -- <command>
  ```
- **Start an interactive shell in a pod:**
  ```bash
  kubectl exec -it <pod-name> -- /bin/bash
  ```

### **Apply/Update Resources**
- **Apply a YAML file (for creating or updating resources):**
  ```bash
  kubectl apply -f <file.yaml>
  ```
- **Delete a resource:**
  ```bash
  kubectl delete -f <file.yaml>
  ```
- **Delete a specific resource:**
  ```bash
  kubectl delete <resource-type> <resource-name>
  ```

### **Context and Configuration**
- **Set default context:**
  ```bash
  kubectl config use-context <context-name>
  ```
- **View current context:**
  ```bash
  kubectl config current-context
  ```

### **Others**
- **Run a pod with a single container:**
  ```bash
  kubectl run <pod-name> --image=<image-name> --restart=Never
  ```
- **Port-forward a pod:**
  ```bash
  kubectl port-forward <pod-name> <local-port>:<pod-port>
  ```

You can always refer to the [official Kubernetes docs](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) for more detailed commands.Here's a concise `kubectl` cheat sheet to help with everyday tasks:

### **Cluster Info**
- **Get cluster info:**
  ```bash
  kubectl cluster-info
  ```
- **Get nodes in the cluster:**
  ```bash
  kubectl get nodes
  ```

### **Namespaces**
- **List namespaces:**
  ```bash
  kubectl get namespaces
  ```
- **Switch namespace:**
  ```bash
  kubectl config set-context --current --namespace=<namespace-name>
  ```

### **Pods**
- **List pods:**
  ```bash
  kubectl get pods
  ```
- **Get pods in all namespaces:**
  ```bash
  kubectl get pods --all-namespaces
  ```
- **Get detailed information about a pod:**
  ```bash
  kubectl describe pod <pod-name>
  ```
- **View pod logs:**
  ```bash
  kubectl logs <pod-name>
  ```
- **View logs of a specific container in a pod:**
  ```bash
  kubectl logs <pod-name> -c <container-name>
  ```
- **Get pod logs since a certain time:**
  ```bash
  kubectl logs <pod-name> --since=1h
  ```
- **Get all logs from all pods in a namespace:**
  ```bash
  kubectl logs -l app=<app-name> --all-containers=true
  ```

### **Deployments**
- **List deployments:**
  ```bash
  kubectl get deployments
  ```
- **Scale a deployment:**
  ```bash
  kubectl scale deployment <deployment-name> --replicas=<number-of-replicas>
  ```
- **Update a deployment:**
  ```bash
  kubectl set image deployment/<deployment-name> <container-name>=<new-image>
  ```
  
### **Services**
- **List services:**
  ```bash
  kubectl get services
  ```
- **Get detailed service info:**
  ```bash
  kubectl describe service <service-name>
  ```
- **Get service endpoint:**
  ```bash
  kubectl get svc <service-name> -o wide
  ```

### **ConfigMaps and Secrets**
- **Get ConfigMaps:**
  ```bash
  kubectl get configmaps
  ```
- **Get a specific ConfigMap:**
  ```bash
  kubectl describe configmap <configmap-name>
  ```
- **Get Secrets:**
  ```bash
  kubectl get secrets
  ```
- **Get a specific secret:**
  ```bash
  kubectl describe secret <secret-name>
  ```

### **Pods and Containers**
- **Execute a command in a running container:**
  ```bash
  kubectl exec -it <pod-name> -- <command>
  ```
- **Start an interactive shell in a pod:**
  ```bash
  kubectl exec -it <pod-name> -- /bin/bash
  ```

### **Apply/Update Resources**
- **Apply a YAML file (for creating or updating resources):**
  ```bash
  kubectl apply -f <file.yaml>
  ```
- **Delete a resource:**
  ```bash
  kubectl delete -f <file.yaml>
  ```
- **Delete a specific resource:**
  ```bash
  kubectl delete <resource-type> <resource-name>
  ```

### **Context and Configuration**
- **Set default context:**
  ```bash
  kubectl config use-context <context-name>
  ```
- **View current context:**
  ```bash
  kubectl config current-context
  ```

### **Others**
- **Run a pod with a single container:**
  ```bash
  kubectl run <pod-name> --image=<image-name> --restart=Never
  ```
- **Port-forward a pod:**
  ```bash
  kubectl port-forward <pod-name> <local-port>:<pod-port>
  ```

You can always refer to the [official Kubernetes docs](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) for more detailed commands.