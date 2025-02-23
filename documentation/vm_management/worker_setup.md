1. **Disable IPv6 Entirely:**  
   If you really need to remove all IPv6 functionality (including link-local addresses), you can disable the IPv6 kernel module entirely using a GRUB parameter:
   - Edit `/etc/default/grub`:
     ```bash
     sudo vim /etc/default/grub
     ```
   - Modify the `GRUB_CMDLINE_LINUX` line to include:
     ```bash
     GRUB_CMDLINE_LINUX="ipv6.disable=1"
   - Update GRUB and reboot
     ```bash
     sudo update-grub
     sudo reboot
     ```

2. **Disable Swap:**
The error message clearly indicates that the kubelet is refusing to start because swap is enabled on your system. Kubernetes does not support running with swap enabled by default.

To fix this, you need to disable swap on your node. Here’s how to do it step-by-step:

---

### 1. Temporarily Disable Swap

Run the following command to disable swap immediately:
```bash
sudo swapoff -a
```
This command turns off swap until the next reboot.

---

### 2. Permanently Disable Swap

To ensure that swap remains disabled after a reboot:

1. **Open the fstab file for editing:**
   ```bash
   sudo vim /etc/fstab
   ```
2. **Locate the line(s) that refer to swap.** It might look similar to:
   ```
   /swap.img   none   swap   sw   0  0
   ```
3. **Comment out that line** by adding a `#` at the beginning:
   ```bash
   #/swap.img   none   swap   sw   0  0
   ```
4. **Save the file** (in nano, press Ctrl+X, then Y, and Enter).

---

Below is a complete, end-to-end guide for setting up a Kubernetes cluster on an Ubuntu server using containerd as the container runtime and Calico as the networking (CNI) plugin. This guide covers everything—from system preparation to cluster initialization and Calico installation—assuming you’re setting up a single control-plane (master) node first. You can later join additional worker nodes using the join command output.

---

## 1. Prepare Your System

### a. Update and Upgrade Packages
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### b. Disable Swap  
Kubernetes requires swap to be turned off.
```bash
sudo swapoff -a
```
*To permanently disable swap, edit `/etc/fstab` and comment out any swap entries.*

### c. Load Required Kernel Modules
Ensure that the `br_netfilter` module is loaded:
```bash
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

sudo modprobe br_netfilter
```

### d. Set System Networking Parameters  
Configure sysctl so that bridged traffic is visible to iptables:
```bash
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo sysctl --system
```

---

## 2. Install and Configure containerd

### a. Install containerd
```bash
sudo apt-get update
sudo apt-get install -y containerd
```

### b. Generate Default Configuration  
Create the configuration file:
```bash
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
```

### c. Configure containerd to Use Systemd Cgroup Driver  
Edit `/etc/containerd/config.toml` and locate the section for the `runc` runtime. Under:
```
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
```
ensure you have the line:
```toml
SystemdCgroup = true
```
*You can use your favorite editor (e.g., nano, vim) to modify the file.*

### d. Restart and Enable containerd  
```bash
sudo systemctl restart containerd
sudo systemctl enable containerd
```

---

## 3. Install kubeadm, kubelet, and kubectl

### a. Add the Kubernetes APT Repository

1. **Add Google Cloud’s public signing key:**
   ```bash
   curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
   ```

2. **Add the repository:**
   ```bash
   cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
   ```

### b. Install the Kubernetes Packages
```bash
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
```

### c. Prevent Automatic Updates
Hold the packages at their current version:
```bash
sudo apt-mark hold kubelet kubeadm kubectl
```

---

## 4. Initialize the Kubernetes Control Plane

### a. Initialize the Cluster  
On the master node, run:
```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```
*The `--pod-network-cidr` value is set for Calico. Adjust if you choose another CNI.*

After initialization, note the **kubeadm join** command provided at the end of the output. You will use this later to join worker nodes.

### b. Set Up Local kubeconfig  
Allow your non-root user to use `kubectl`:
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

## 5. Install Calico for Networking

You have two common methods to install Calico:  
- **Method A: Direct Manifest (Simpler)**  
- **Method B: Tigera Operator (Advanced)**

### Method A: Using the Calico Manifest

Apply the official Calico manifest:
```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

Verify that the Calico pods are running:
```bash
kubectl get pods -n kube-system
```
*It may take several minutes for all pods to reach the `Running` state.*

### Method B: Using the Tigera Operator  
Alternatively, if you prefer the operator-based installation:

1. **Deploy the Tigera Operator:**
   ```bash
   kubectl apply -f https://docs.tigera.io/manifests/tigera-operator.yaml
   ```
   Verify the operator pod:
   ```bash
   kubectl get pods -n tigera-operator
   ```

2. **Create a Calico Installation Custom Resource:**  
   Create a file named `calico.yaml` with the following contents:
   ```yaml
   apiVersion: operator.tigera.io/v1
   kind: Installation
   metadata:
     name: default
   spec:
     variant: Calico
     calicoNetwork:
       bgp: Enabled
       ipPools:
       - cidr: 192.168.0.0/16
         encapsulation: VXLAN
         natOutgoing: Enabled
   ```
   Apply the custom resource:
   ```bash
   kubectl apply -f calico.yaml
   ```

3. **Verify the Calico Deployment:**  
   Check the status in the `calico-system` namespace:
   ```bash
   kubectl get pods -n calico-system
   ```
Choose the method that best suits your needs. Method A is quicker and simpler for most setups, while Method B offers more flexibility and management via the operator.

---

## 6. (Optional) Join Worker Nodes

On each worker node, repeat **Sections 1–3** (system preparation, containerd installation, and kubeadm setup). Then run the **kubeadm join** command you saved from the control plane initialization, for example:

```bash
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

---

## 7. Final Verification

On your master node, check the status of your nodes and pods:
```bash
kubectl get nodes
kubectl get pods --all-namespaces
```
You should see your master (and any worker nodes you’ve joined) listed, with all pods—including Calico—running correctly.

---

This completes the full setup of a Kubernetes cluster on an Ubuntu server with containerd and Calico as the networking solution. Enjoy your new cluster!

Below is a step‐by‐step guide for installing Kubernetes on an Ubuntu server using kubeadm with containerd as the container runtime and Calico for networking. This guide assumes you’re setting up a single control plane (master) node first. You can later add worker nodes using the join token generated during initialization.

---

## 1. Prepare Your System

### a. Update and Upgrade
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### b. Disable Swap
Kubernetes requires swap to be disabled.
```bash
sudo swapoff -a
```
To make this change permanent, edit `/etc/fstab` and comment out any swap entries.

### c. Load Necessary Kernel Modules
Ensure required kernel modules are loaded:
```bash
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

sudo modprobe br_netfilter
```

### d. Set System Networking Parameters
Configure sysctl so that iptables can see bridged traffic:
```bash
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo sysctl --system
```

---

## 2. Install containerd

### a. Install containerd
```bash
sudo apt-get update
sudo apt-get install -y containerd
```

### b. Configure containerd
Generate the default configuration file:
```bash
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
```

Edit the configuration file (`/etc/containerd/config.toml`) to set the cgroup driver to systemd. Find the section under `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]` and ensure it includes:
```toml
SystemdCgroup = true
```

### c. Restart and Enable containerd
```bash
sudo systemctl restart containerd
sudo systemctl enable containerd
```

---

## 3. Install kubeadm, kubelet, and kubectl

### a. Add the Kubernetes APT Repository
1. **Add the Google Cloud public signing key:**
   ```bash
   curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
   ```

2. **Add the Kubernetes APT repository:**
   ```bash
   cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
   ```

### b. Install the Packages
```bash
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
```

### c. Hold the Packages at Their Current Version
```bash
sudo apt-mark hold kubelet kubeadm kubectl
```

---

## 4. Initialize the Kubernetes Control Plane

### a. Initialize the Cluster
On your master node, run:
```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```
*Note:* The `--pod-network-cidr` is set for Calico. If you use a different CNI, this may need adjustment.

After the command completes, note the **kubeadm join** command (which will be used to add worker nodes later).

### b. Set Up Local kubeconfig
Configure kubectl for your user:
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

## 5. Install Calico as the CNI Plugin

### a. Apply the Calico Manifest
Calico provides networking and network policy. Run:
```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

### b. Verify Calico Pods
Check that all Calico pods are running:
```bash
kubectl get pods -n kube-system
```
It may take several minutes for all pods to be in a `Running` state.

---

## 6. (Optional) Join Worker Nodes

On each worker node, repeat steps 1–3 and then use the **kubeadm join** command (saved from the master node initialization) to join the cluster:
```bash
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

---

## Final Checks

On your master node, verify the cluster status:
```bash
kubectl get nodes
kubectl get pods --all-namespaces
```
You should see your master (and later worker nodes) listed, with Calico and other pods running as expected.

---

This completes your step-by-step installation of Kubernetes with kubeadm using containerd and Calico on an Ubuntu server. Happy clustering!

Below is a step‐by‐step guide that assumes you already have your Kubernetes cluster initialized (using kubeadm with containerd, as in your previous setup) and now want to install Calico via the latest Tigera Operator method.

---

## 1. Install the Tigera Operator

The Tigera Operator manages the installation and lifecycle of Calico on your cluster. Run the following command:

```bash
kubectl apply -f https://docs.tigera.io/manifests/tigera-operator.yaml
```

Wait a few moments and then verify that the operator pod is running in the `tigera-operator` namespace:

```bash
kubectl get pods -n tigera-operator
```

---

## 2. Create the Calico Installation Custom Resource

The Operator deploys Calico based on the desired configuration specified in a custom resource. Create a file (e.g. `calico.yaml`) with contents similar to the example below. Adjust the configuration if needed for your environment.

```yaml
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  variant: Calico
  calicoNetwork:
    bgp: Enabled
    ipPools:
    - cidr: 192.168.0.0/16
      encapsulation: VXLAN
      natOutgoing: Enabled
```

Once you’ve saved the file, apply it with:

```bash
kubectl apply -f calico.yaml
```

The Operator will read this custom resource and start deploying the necessary components.

---

## 3. Verify Calico Deployment

Monitor the progress by checking the pods in the `calico-system` namespace:

```bash
kubectl get pods -n calico-system
```

All Calico pods should eventually be in a `Running` state. You can also check the status of the installation custom resource with:

```bash
kubectl get installation
```

---

## 4. Final Checks

After the installation has completed, verify that your nodes and pods are ready:

```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

This confirms that Calico is now managing pod networking and network policy for your Kubernetes cluster using the latest operator-based installation.

---

This completes the installation of Calico with the Tigera Operator as described in the official documentation. If you need to adjust network settings or further customize the installation, refer to the [Calico on Kubernetes documentation](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises#install-calico) for additional options and details.