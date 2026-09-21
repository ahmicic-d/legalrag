interface Props {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export default function PageHeader({ eyebrow, title, description, actions }: Props) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-line pb-6">
      <div>
        <div className="eyebrow mb-1">{eyebrow}</div>
        <h1 className="page-title">{title}</h1>
        {description && <p className="mt-2 max-w-2xl text-sm text-ink/60">{description}</p>}
      </div>
      {actions}
    </div>
  );
}
