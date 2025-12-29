import random, math
from collections import deque

# Fixer la graine (seed) aléatoire pour garantir la reproductibilité :
# à chaque exécution, les tirages random (population initiale, mutation, tournoi, crossover…) seront identiques.
random.seed(42)

# Facteur de seniorité : on multiplie la vitesse “brute” d’un développeur par ce coefficient (comme dans l’article).
LEVEL_FACTOR={"junior":.8,"engineer":1.0,"manager":1.1,"director":1.2}

# ---------- Structures de données ----------
# Un développeur = (id, compétences par type de tâche, niveau/seniorité).
class Developer: 
    def __init__(s,id,ab,lv): 
        s.id=id; s.abilities=ab; s.level=lv

# Une tâche = (id, type, effort à réaliser, liste de prérequis).
class Task:
    def __init__(s,id,typ,eff,pre): 
        s.id=id; s.typ=typ; s.effort=eff; s.prereq=list(pre)

# ---------- Jeu de données de test : Set1 ----------
def generate_set1_data():
    # Liste des développeurs avec leurs vitesses par type et leur niveau.
    devs=[Developer("d1",{"analysis":1.25,"design":1.0,"implementation":1.25,"testing":1.25},"director"),
          Developer("d2",{"analysis":1.25,"design":1.0,"implementation":1.25,"testing":0.75},"director"),
          Developer("d3",{"analysis":0.75,"design":0.75,"implementation":1.0,"testing":1.0},"manager"),
          Developer("d4",{"analysis":0.75,"design":1.0,"implementation":1.0,"testing":0.75},"manager"),
          Developer("d5",{"analysis":1.0,"design":0.75,"implementation":0.75,"testing":1.0},"engineer"),
          Developer("d6",{"analysis":0.75,"design":1.0,"implementation":0.75,"testing":0.75},"engineer"),
          Developer("d7",{"analysis":1.0,"design":0.75,"implementation":1.0,"testing":0.75},"engineer")]
   
    # Dictionnaire des tâches : effort + dépendances (prérequis).
    tasks={"t1":Task("t1","analysis",400,[]),
           "t2":Task("t2","design",320,["t1"]),
           "t3":Task("t3","design",240,["t1"]),
           "t4":Task("t4","design",240,["t1"]),
           "t5":Task("t5","implementation",240,["t2"]),
           "t6":Task("t6","implementation",600,["t3"]),
           "t7":Task("t7","implementation",160,["t4"]),
           "t8":Task("t8","testing",100,["t5"]),
           "t9":Task("t9","testing",80,["t6"]),
           "t10":Task("t10","testing",70,["t7"]),
           "t11":Task("t11","testing",80,["t8","t9","t10"])}
    return tasks, devs

# ---------- Algorithme génétique (GA) ----------
def ga(tasks, devs, W, pop=20, gens=50, mut=0.03, tourn=3, elit=2, kmax=3, verbose=True):
    # Indexation (TaskID->index, DevID->index) pour accélérer les calculs en tableaux.
    tids=list(tasks); tidx={t:i for i,t in enumerate(tids)}; nT=len(tids)
    dids=[d.id for d in devs]; didx={d:i for i,d in enumerate(dids)}; nD=len(dids)

    # Infos utiles pour BA (balance par niveaux).
    dev_level={d.id:d.level for d in devs}; levels=sorted(set(d.level for d in devs))

    # Construction du graphe de dépendances des tâches + effort.
    effort=[0.0]*nT; prereq=[[] for _ in range(nT)]; adj=[[] for _ in range(nT)]
    for tid,t in tasks.items():
        i=tidx[tid]                            # index de la tâche tid
        effort[i]=float(t.effort)              # effort numérique
        prereq[i]=[tidx[p] for p in t.prereq]  # prérequis sous forme d’indices
        for p in prereq[i]: adj[p].append(i)   # adj[p] contient les successeurs de p

    # Matrice speed[dev_index][task_index] = vitesse effective (compétence * LEVEL_FACTOR).
    speed=[[0.0]*nT for _ in range(nD)]
    for d in devs:
        di=didx[d.id]; lf=LEVEL_FACTOR.get(d.level,1.0)
        for tid,t in tasks.items():
            speed[di][tidx[tid]]=d.abilities.get(t.typ,0.0)*lf

    # Pénalité de coordination quand k développeurs travaillent sur la même tâche (rendements décroissants).
    coord=lambda k: 1.0 if k<=1 else max(0.4,1.0-0.12*(k-1))

    # Nettoyage d’un chromosome (allocation tâches->devs) :
    # - supprime doublons, - supprime IDs invalides, - limite à kmax devs/tâche, - garantit ≥1 dev/tâche.
    def sanitize(ch):
        for tid in tids:
            seen=set(); out=[]
            for d in ch.get(tid,[]):
                if d in didx and d not in seen:
                    seen.add(d); out.append(d)
            ch[tid]=out[:kmax] if out else [random.choice(dids)]
        return ch

    # Borne optimiste minTS (chemin critique) :
    # on suppose que chaque tâche est faite par le meilleur développeur possible pour son type.
    def minTS():
        best=[]
        for ti in range(nT):
            best_sp=max(speed[di][ti] for di in range(nD))
            best.append(effort[ti]/best_sp if best_sp>0 else float("inf"))
        indeg=[len(prereq[i]) for i in range(nT)]
        q=deque([i for i in range(nT) if indeg[i]==0])
        dp=best[:]  # dp[i] = durée max pour atteindre i (chemin le plus long)
        seen=0
        while q:
            u=q.popleft(); seen+=1
            for v in adj[u]:
                dp[v]=max(dp[v], dp[u]+best[v])
                indeg[v]-=1
                if indeg[v]==0: q.append(v)
        return max(dp) if seen==nT else min(best)*nT

    MIN_TS=minTS()

    # Simulateur discret : exécute les tâches “enabled” à chaque tick, applique multitâche + coordination,
    # renvoie (finish_time, dev_stats).
    def simulate(ch, max_ticks=20000):
        rem=effort[:]                                   # effort restant
        done=[False]*nT                                  # tâches terminées ?
        need=[len(prereq[i]) for i in range(nT)]         # nb de prérequis restants
        enabled=[i for i in range(nT) if need[i]==0 and rem[i]>0]

        load=[0]*nD                                      # load[dev]=nb tâches simultanées ce tick
        tw=[0]*nD; tm=[0]*nD                              # ticks_with_work / ticks_with_multitask
        t=0; done_cnt=0

        while done_cnt<nT and t<max_ticks:
            if not enabled: t+=1; continue

            # Calcul de la charge par dev (multitâche) sur ce tick.
            for di in range(nD): load[di]=0
            for ti in enabled:
                for d in ch[tids[ti]]:
                    di=didx.get(d)
                    if di is not None: load[di]+=1

            # Stats CE : nombre de ticks où le dev travaille / multitâche.
            for di in range(nD):
                if load[di]>0:
                    tw[di]+=1
                    if load[di]>1: tm[di]+=1

            # Avancement des tâches enabled.
            finished=[]
            for ti in enabled:
                raw=0.0; cnt=0
                for d in ch[tids[ti]]:
                    di=didx.get(d)
                    if di is None: continue
                    raw += speed[di][ti]/(load[di] if load[di] else 1)  # partage de vitesse si multitâche
                    cnt += 1
                if cnt:
                    rem[ti]-=raw*coord(cnt)                             # pénalité coordination
                    if rem[ti]<=0 and not done[ti]:
                        done[ti]=True; finished.append(ti); done_cnt+=1

            # Débloquer les successeurs quand des tâches finissent.
            if finished:
                fin=set(finished)
                enabled=[x for x in enabled if x not in fin]
                for u in finished:
                    for v in adj[u]:
                        need[v]-=1
                        if need[v]==0 and (not done[v]) and rem[v]>0:
                            enabled.append(v)
            t+=1

        return t, {dids[i]:{"ticks_with_work":tw[i],"ticks_with_multitask":tm[i]} for i in range(nD)}

    # Calcule les scores CM, CE, CC, BA + fitness globale (pondérée).
    def score(ch):
        ch=sanitize(ch)
        finish, ds = simulate(ch)

        # CM (makespan) = minTS / max(finish_time, minTS)
        cm=0.0 if MIN_TS<=0 or math.isinf(MIN_TS) else MIN_TS/max(finish,MIN_TS)

        # CE (concentration) : 1 - (ticks multitâche / ticks travaillés) moyenné sur les devs.
        ce=sum(1.0 if ds[d]["ticks_with_work"]==0 else max(0.0,1.0-ds[d]["ticks_with_multitask"]/ds[d]["ticks_with_work"])
               for d in dids)/nD

        # CC (continuity) : fraction de relations (préreq->tâche) qui partagent au moins 1 développeur.
        total=ok=0
        for tid,t in tasks.items():
            for p in t.prereq:
                total+=1
                ok += 1 if (set(ch[tid]) & set(ch[p])) else 0
        cc=ok/total if total else 1.0

        # BA (balance) : entropie normalisée de la distribution des efforts par niveau de staff.
        ba_vals=[]
        for lvl in levels:
            nums=[sum(1 for d in ch[tid] if dev_level.get(d)==lvl)*tasks[tid].effort for tid in tids]
            denom=sum(nums)
            if denom==0: ba_vals.append(1.0); continue
            ps=[x/denom for x in nums if x>0]
            ba_vals.append(-sum(p*(math.log(p)/math.log(nT)) for p in ps))
        ba=sum(ba_vals)/len(ba_vals) if ba_vals else 0.0

        # Fitness finale (pondérations W).
        fit=W["cm"]*cm+W["ce"]*ce+W["cc"]*cc+W["ba"]*ba
        return fit, {"cm":cm,"ce":ce,"cc":cc,"ba":ba,"sim":{"finish_time":finish,"dev_stats":ds}}

    # Initialisation aléatoire de la population (chromosomes).
    init=lambda: [sanitize({tid: random.sample(dids, random.randint(1,kmax)) for tid in tids}) for _ in range(pop)]

    # Sélection tournoi : on choisit le meilleur parmi “tourn” individus tirés au hasard.
    pick=lambda P,F: (lambda b: {tid:P[b][tid][:] for tid in tids})(
        max(random.sample(range(pop),tourn), key=lambda i:F[i])
    )

    # Crossover uniforme : pour chaque tâche, on copie le gène du parent1 ou du parent2.
    cross=lambda a,b: {tid:(a[tid][:] if random.random()<0.5 else b[tid][:]) for tid in tids}

    # Mutation : add/remove/replace un développeur sur certaines tâches, puis sanitize.
    def mutate(ch):
        for tid in tids:
            if random.random()<mut:
                op=random.choice(["add","remove","replace"])
                if op=="add" and len(ch[tid])<kmax:
                    cand=[d for d in dids if d not in ch[tid]]
                    if cand: ch[tid].append(random.choice(cand))
                elif op=="remove" and len(ch[tid])>1:
                    ch[tid].pop(random.randrange(len(ch[tid])))
                elif op=="replace":
                    i=random.randrange(len(ch[tid]))
                    cand=[d for d in dids if d not in ch[tid]]
                    if cand: ch[tid][i]=random.choice(cand)
        return sanitize(ch)

    # ----- Boucle GA -----
    P=init()
    F,D=zip(*(score(ch) for ch in P)); F=list(F); D=list(D)
    b=max(range(pop), key=lambda i:F[i]); best=(P[b],F[b],D[b])

    for g in range(gens):
        # Elitisme : conserver les meilleurs individus sans modification.
        r=sorted(range(pop), key=lambda i:F[i], reverse=True)
        newP=[P[i] for i in r[:elit]]
        newF=[F[i] for i in r[:elit]]
        newD=[D[i] for i in r[:elit]]

        # Générer le reste par sélection + crossover + mutation.
        while len(newP)<pop:
            c=mutate(cross(pick(P,F), pick(P,F)))
            f,d=score(c)
            newP.append(c); newF.append(f); newD.append(d)

        P,F,D=newP,newF,newD
        b=max(range(pop), key=lambda i:F[i])
        if F[b]>best[1]: best=(P[b],F[b],D[b])
        if verbose: print(f"Gen {g+1}/{gens} best fitness: {best[1]:.4f}")

    return best

# Somme globale des ticks de multitâche (pour la colonne "Multitask" du tableau).
multitask_sum=lambda det: sum(v["ticks_with_multitask"] for v in det["sim"]["dev_stats"].values())

if __name__=="__main__":
    tasks, devs = generate_set1_data()

    # ----- CaseAll : pondérations égales
    chromA, fitA, detA = ga(tasks, devs, {"cm":.25,"ce":.25,"cc":.25,"ba":.25})
    # ----- CaseTime : optimiser uniquement le makespan (CM)
    chromT, fitT, detT = ga(tasks, devs, {"cm":1.0,"ce":0.0,"cc":0.0,"ba":0.0})

    timeA,multiA = detA["sim"]["finish_time"], multitask_sum(detA)
    timeT,multiT = detT["sim"]["finish_time"], multitask_sum(detT)

    print("=== COMPARISON TABLE ===")
    print(f"{'Set':<6} | {'Time(All)':>10} | {'Time(Time)':>10} | {'Multitask(All)':>15} | {'Multitask(Time)':>15}")
    print(f"{'Set1':<6} | {timeA:>10.2f} | {timeT:>10.2f} | {multiA:>15.2f} | {multiT:>15.2f}")

    print("\n=== BEST SOLUTION (CaseAll) ===")
    print("Best fitness:", round(fitA, 6))
    print("Components:", {k: round(v, 6) for k, v in detA.items() if k in ["cm","ce","cc","ba"]})
    print("Finish time (sim):", detA["sim"]["finish_time"])
    print("Assignments (task -> devs):")
    for tid in sorted(chromA, key=lambda x:int(x[1:])): print(f"  {tid} -> {chromA[tid]}")

    print("\n=== BEST SOLUTION (CaseTime) ===")
    print("Best fitness:", round(fitT, 6))
    print("Finish time (sim):", detT["sim"]["finish_time"])
    print("Assignments (task -> devs):")
    for tid in sorted(chromT, key=lambda x:int(x[1:])): print(f"  {tid} -> {chromT[tid]}")